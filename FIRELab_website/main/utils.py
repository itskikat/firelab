import base64
import numpy as np
import cv2
from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000
from osgeo import gdal, osr
from main.models import Tile, Grid
import math


def opencv_to_base64(img, ext):
    _, im_arr = cv2.imencode('.' + ext, img)  # Numpy one-dim array representative of the img
    im_bytes = im_arr.tobytes()
    im_b64 = base64.b64encode(im_bytes)
    return im_b64


def base64_to_opencv(im_b64):
    im_bytes = base64.b64decode(im_b64)
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # Numpy one-dim array representative of the img
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
    return img


def ortophoto_transformation_pixel_to_coordinate(tif_path, x, y):
    src = gdal.Open(tif_path)
    x_ul, x_res, x_skew, y_ul, y_skew, y_res = src.GetGeoTransform()

    _x = x_ul + x * x_res + y * x_skew
    _y = y_ul + y * y_res + x * y_skew

    return _x, _y

    # source = osr.SpatialReference()
    # source.ImportFromWkt(src.GetProjection())
    #
    # # The target projection - WGS84 mainly favoured in GPSs
    # target = osr.SpatialReference()
    # target.ImportFromEPSG(4326)
    #
    # # Create the transform
    # transform = osr.CoordinateTransformation(source, target)
    # long, lat, rot = transform.TransformPoint(_x, _y)
    # # first comes longitude and then latitude (and rotation in the end?)
    # return lat, long, rot


def ortophoto_transformation_coordinate_to_pixel(tif_path, lat, lon):
    src = gdal.Open(tif_path)

    # source = osr.SpatialReference()
    # source.ImportFromEPSG(4326)
    #
    # # The target projection - WGS84 mainly favoured in GPSs
    # target = osr.SpatialReference()
    # target.ImportFromWkt(src.GetProjection())
    #
    # transform = osr.CoordinateTransformation(source, target)
    # _x, _y, rot = transform.TransformPoint(lon, lat)

    x_ul, x_res, x_skew, y_ul, y_skew, y_res = src.GetGeoTransform()

    # assuming that the rotation in x and y are both 0 we have
    x = (lat - x_ul)/x_res
    y = (lon - y_ul)/y_res

    return round(x), round(y)


def pixel_average(rgb1, rgb2):
    avg=[]
    for i in range(3):
        avg.append((rgb1[i]+rgb2[i])/2)
    return avg


def cell_cutter(tif_path, row, column, top_left_x, top_left_y, bottom_right_x, bottom_right_y, grid_id):
    img = gdal.Open(tif_path)

    diff_x = int((bottom_right_x - top_left_x))
    diff_y = int((bottom_right_y - top_left_y))

    print("Diferences:", diff_x, diff_y)            # pixels
    print(column, row)                              # ints

    band_r = img.GetRasterBand(1)
    band_g = img.GetRasterBand(2)
    band_b = img.GetRasterBand(3)

    img_r = band_r.ReadAsArray(int(top_left_x), int(top_left_y), diff_x, diff_y)
    img_g = band_g.ReadAsArray(int(top_left_x), int(top_left_y), diff_x, diff_y)
    img_b = band_b.ReadAsArray(int(top_left_x), int(top_left_y), diff_x, diff_y)

    img = np.dstack((img_b, img_g, img_r))

    jump_x, jump_y = int(diff_x/column), int(diff_y/row)
    print(jump_x, jump_y)

    for y in range(0, diff_y, jump_y):
        for x in range(0, diff_x, jump_x):
            position = (int((x % diff_x) / jump_x), int((y % diff_y) / jump_y))

            matrix = img[y:y + jump_x, x:x + jump_y]

            tile = matrix
            tile_y = tile[0].tolist()
            tile_x = tile[1].tolist()

            avgColor = None
            for _y in tile_y:
                if avgColor is None:
                    avgColor = _y
                else:
                    avgColor = pixel_average(avgColor, _y)

            for _x in tile_x:
                avgColor = pixel_average(avgColor, _x)

            try:
                _grid = Grid.objects.get(id=grid_id)
            except Grid.DoesNotExist:
                return None

            tile = Tile(
                position=position,
                classification=None,
                avgColor=[int(avgColor[0]), int(avgColor[1]), int(avgColor[2])],
                grid=_grid
            )
            print(tile)
            tile.save()


def draw_grid(mask, step, top_left, bottom_right, line_color=(255, 0, 0), thickness=1, type_=cv2.LINE_AA):
    x = top_left[0]
    y = top_left[1]

    while x <= bottom_right[0]:
        cv2.line(mask, (x, top_left[1]), (x, bottom_right[1]), color=line_color, lineType=type_, thickness=thickness)
        x += step

    while y <= bottom_right[1]:
        cv2.line(mask, (top_left[0], y), (bottom_right[0], y), color=line_color, lineType=type_, thickness=thickness)
        y += step

    return mask

    # # crop mask
    # mask = mask[1052:2332, 865:1735]
    #
    # scale_percent = 50  # percent of original size
    # width = int(mask.shape[1] * scale_percent / 100)
    # height = int(mask.shape[0] * scale_percent / 100)
    # dim = (width, height)
    #
    # # resize image
    # resized = cv2.resize(mask, dim, interpolation=cv2.INTER_AREA)
    #
    # print('Resized Dimensions : ', resized.shape)
    #
    # cv2.imshow("Resized image", resized)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


def distance(rgb1, rgb2):
    return math.sqrt(
        math.pow((rgb1[0] - rgb2[0]), 2) + math.pow((rgb1[1] - rgb2[1]), 2) + math.pow((rgb1[2] - rgb2[2]), 2))


def numerically_closest(tile, means):
    distances = [distance(tile.avgColor, mean) for mean in means]

    _min = distances[0]
    min_index = 0

    for i in range(1, len(distances)):
        if _min > distances[i]:
            _min = distances[i]
            min_index = i

    return min_index


def visually_closest(tile, lab_colors):
    tile_avgColor = sRGBColor(tile.avgColor[0], tile.avgColor[1], tile.avgColor[2])

    # convert tile avgColor to lab format
    tile_lab_avgColor = convert_color(tile_avgColor, LabColor)

    # calculate difference using the lab method
    distances = [delta_e_cie2000(tile_lab_avgColor, lab_color) for lab_color in lab_colors]

    _min = distances[0]
    min_index = 0

    for i in range(1, len(distances)):
        if _min > distances[i]:
            _min = distances[i]
            min_index = i

    return min_index


def simplified_pixel_average(tile_list):
    return [
        sum([c[0] for c in [t.avgColor for t in tile_list]]) / len(tile_list),
        sum([c[1] for c in [t.avgColor for t in tile_list]]) / len(tile_list),
        sum([c[2] for c in [t.avgColor for t in tile_list]]) / len(tile_list)
    ]
