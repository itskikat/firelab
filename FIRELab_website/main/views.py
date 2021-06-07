import concurrent.futures
import io
import json
import math
import pickle
import time
from datetime import datetime, timedelta

from django.core.files import File
from django.core.files.images import ImageFile
from django.shortcuts import render, redirect
from django.contrib.gis.geos import Polygon, LinearRing
from django.db.models import Q, Min, Max


from FIRELab_website.settings import MEDIA_ROOT
from main import utils
from main.forms import *
import cv2
import os
import numpy as np
from django.http import HttpResponse, FileResponse
from osgeo import gdal


# Create your views here.
def indexView(response):
    return render(response, "main/home.html", {})


# Create new user account
def createAccountView(request):
    data = {}
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            print(form)
            user = form.save()
            user.refresh_from_db()
            return redirect('login')
    else:
        form = CreateAccountForm()
        data['form'] = form
    return render(request, 'main/signup.html', data)


def projects(request):
    if request.user.is_authenticated:
        project_list = Project.objects.all().filter(owner=request.user)

        if request.method == 'POST':
            creation_form = ProjectCreation(request.POST)
            if creation_form.is_valid():
                new_project = Project(
                    name=creation_form.cleaned_data['name'],
                    description=creation_form.cleaned_data['description'],
                    owner=request.user
                )
                new_project.save()

                root = Directory(
                    name='root',
                    project=new_project
                )
                root.save()

                for d in ['Images', 'Ortophotos', 'Frames', 'Grids']:
                    _d = Directory(
                        name=d,
                        project=new_project,
                        parent=root
                    )
                    _d.save()

                creation_form = ProjectCreation()

        else:
            creation_form = ProjectCreation()

        params = {
            'project_list': project_list,
            'creation_form': creation_form
        }

        return render(request, "main/projects.html", params)


def account(response):
    return render(response, "main/account.html", {})


def process(response, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return redirect("/projects")

    param = {
        'project': project,
        'project_dirs': Directory.objects.all().filter(project_id=project.id),
        'project_files': FileInfo.objects.all().filter(dir__project_id=project.id),
    }
    return render(response, "main/project_process.html", param)


def vegetation(response, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return redirect("/projects")

    if response.method == "GET":

        ortophoto_form = UploadOrtophoto()
        grid_draw_form = DrawGridForm()
        manual_classifier_form = ManualClassifierForm()

        param = {
            'project': project,
            'project_dirs': Directory.objects.all().filter(project_id=project.id),
            'project_files': FileInfo.objects.all().filter(dir__project_id=project.id),
            'ortophoto_form': ortophoto_form,
            'grid_draw': grid_draw_form,
            'manual_classifier_form': manual_classifier_form
        }

        if 'id' in response.GET or 'grid' in response.GET:

            try:
                if 'id' in response.GET:
                    _ortophoto = Ortophoto.objects.get(file_info_id=response.GET['id'])
                else:
                    _ortophoto = Ortophoto.objects.get(grid__file_info_id=response.GET['grid'])

            except Ortophoto.DoesNotExist:
                return redirect("/projects/" + str(project_id) + "/vegetation")

            if _ortophoto.thumbnail:
                param['image'] = _ortophoto

            else:
                print("Image doesn't exist -- creating thumbnail")
                ortophoto = gdal.Open(os.path.abspath(os.path.join(MEDIA_ROOT, _ortophoto.content.name)))

                options_list = [
                    '-of PNG',
                    '-outsize 10% 10%'
                ]
                options_string = " ".join(options_list)
                gdal.Translate(
                    os.path.abspath(
                        os.path.join(MEDIA_ROOT, "ortophotos/{}_thumbnail.png".format(_ortophoto.file_info.name))),
                    ortophoto,
                    options=options_string
                )

                file = File(open(
                    os.path.abspath(
                        os.path.join(MEDIA_ROOT, "ortophotos/{}_thumbnail.png".format(_ortophoto.file_info.name))),
                    "rb"))
                _ortophoto.thumbnail.save("{}_thumbnail.png".format(_ortophoto.file_info.name), file)
                os.remove(os.path.abspath(
                    os.path.join(MEDIA_ROOT, "ortophotos/{}_thumbnail.png".format(_ortophoto.file_info.name))))
                os.remove(os.path.abspath(
                    os.path.join(MEDIA_ROOT, "ortophotos/{}_thumbnail.png.aux.xml".format(_ortophoto.file_info.name))))
                param['image'] = _ortophoto

        if 'grid' in response.GET:
            # verify if grid exists
            try:
                _grid = Grid.objects.get(ortophoto=_ortophoto, file_info_id=int(response.GET['grid']))
                param['grid'] = _grid
            except Grid.DoesNotExist:
                return render(response, "main/vegetation_characterization.html", param)

            _top_left = _grid.topLeftCoordinate
            _bottom_right = _grid.bottomRightCoordinate
            top_left = [int(e * 0.10) for e in _top_left]
            bottom_right = [int(e * 0.10) for e in _bottom_right]

            tiles = Tile.objects.all().filter(grid_id=_grid.id)
            x_pos = max([t.position[0] for t in tiles])
            cell_size = int((bottom_right[0] - top_left[0]) / (x_pos + 1))

            # DRAW GRID #
            if not _grid.gridded_image:
                # No gridded image - must be created and stored in db
                img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _ortophoto.thumbnail.name)))

                gridded_image = utils.draw_grid(img, cell_size, top_left, bottom_right)
                gridded_image[np.where((gridded_image == [0, 0, 0]).all(axis=2))] = [255, 255, 255]

                path = os.path.abspath(os.path.join(MEDIA_ROOT, "grids/grid_{}_aux.png".format(_grid.file_info.name)))
                cv2.imwrite(path, gridded_image)

                file = File(open(path, "rb"))
                _grid.gridded_image.save("grid_{}.png".format(_grid.file_info.name), file)
                os.remove(path)

            else:
                # get image from db
                gridded_image = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _grid.gridded_image.name)))

            param['gridded_image'] = _grid.gridded_image

            # DRAW IMAGE WITH JUST THE WANTED FILTERS
            classification_total = Classification.objects.all().filter(model=_grid.model)

            for index in range(0, len(classification_total)):
                if str(index) in response.GET and response.GET[str(index)] == 'hidden':
                    tiles = tiles.filter(~Q(classification=index))
                    print("hide level", str(index))

            to_classify = gridded_image[top_left[1]:bottom_right[1], top_left[0]: bottom_right[0]]
            mask = np.zeros(to_classify.shape[:2], np.uint8)
            mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

            tiles = tiles.filter(classification__isnull=False)

            shape = to_classify.shape[:2]
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(classification_total)) as executor:
                future_mask = {
                    executor.submit(utils.compute_mask, tiles.filter(classification=classification_index), cell_size, classification_total.filter(classificationIndex=classification_index).first(), shape): classification_index
                    for classification_index in range(0, len(classification_total))
                }

                done, _ = concurrent.futures.wait(future_mask, timeout=20, return_when=concurrent.futures.ALL_COMPLETED)

                for future in done:
                    mask = mask + future.result()

            # print("start draw loop on", len(tiles), 'tiles')
            # start = time.time()
            # for tile in tiles:
            #     test_tile = tile.position
            #     start_point = (test_tile[0] * cell_size, test_tile[1] * cell_size)
            #     end_point = (start_point[0] + cell_size, start_point[1] + cell_size)
            #
            #     if tile.classification < len(classification_total):
            #         color = classification_total.filter(classificationIndex=tile.classification).first().hexColor
            #         rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
            #         mask = cv2.rectangle(mask, start_point, end_point, (rgb[2], rgb[1], rgb[0]), -1)
            # end = time.time()
            # print("Mask creation without threading:", end-start)

            classified_img = cv2.addWeighted(to_classify, 0.5, mask, 0.5, 0, dtype=cv2.CV_8UC3)
            gridded_image[top_left[1]:bottom_right[1], top_left[0]: bottom_right[0]] = classified_img

            gridded_image_base64 = utils.opencv_to_base64(gridded_image, 'png')
            param['gridded_image'] = 'data:image/png;base64,{image}'.format(image=gridded_image_base64.decode())
            param["model"] = Classification.objects.all().filter(model=_grid.model)

        return render(response, "main/vegetation_characterization.html", param)

    else:

        grid_draw_form = DrawGridForm(response.POST)
        manual_classifier_form = ManualClassifierForm(response.POST)

        # drawing the grid on the ortophoto
        if grid_draw_form.is_valid():
            image_id = grid_draw_form.cleaned_data['image_id']
            try:
                _ortophoto = Ortophoto.objects.get(file_info_id=image_id)
            except Ortophoto.DoesNotExist:
                return redirect("/projects/" + str(project_id) + "/vegetation")

            img_width, img_height = grid_draw_form.cleaned_data['image_size'].split(", ")
            p1_x, p1_y = grid_draw_form.cleaned_data['p1'].split(", ")
            p2_x, p2_y = grid_draw_form.cleaned_data['p2'].split(", ")

            img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _ortophoto.thumbnail.name)))
            real_height, real_width = img.shape[:2]

            # factor is the multiplication factor between the dimensions in the frontend and the image's real dimensions
            # multiplied by 10 because the map is compressed 10% to create the png
            x_factor, y_factor = real_width / int(img_width), real_height / int(img_height)
            p1_x, p1_y = math.floor(int(p1_x) * x_factor) * 10, math.floor(int(p1_y) * y_factor) * 10
            p2_x, p2_y = math.floor(int(p2_x) * x_factor) * 10, math.floor(int(p2_y) * y_factor) * 10

            if p1_x > p2_x:
                p1_x, p2_x = p2_x, p1_x

            if p1_y > p2_y:
                p1_y, p2_y = p2_y, p1_y

            ortophoto_path = os.path.join(MEDIA_ROOT, _ortophoto.content.name)
            # in meters
            x1_m, y1_m = utils.ortophoto_transformation_pixel_to_coordinate(ortophoto_path, p1_x, p1_y)
            x2_m, y2_m = utils.ortophoto_transformation_pixel_to_coordinate(ortophoto_path, p2_x, p2_y)

            diff_x, diff_y = x2_m - x1_m, y2_m - y1_m

            CELL_SIZE = 5  # in meters TODO: MAKE DYNAMIC
            patch_x = diff_x % CELL_SIZE  # value to remove to lat2
            x2_m -= patch_x

            patch_y = diff_y % CELL_SIZE
            y2_m -= patch_y

            p2_x, p2_y = utils.ortophoto_transformation_coordinate_to_pixel(ortophoto_path, x2_m, y2_m)

            column = int(abs(diff_x // CELL_SIZE))
            row = int(abs(diff_y // CELL_SIZE))

            _file_info = FileInfo(
                name=_ortophoto.file_info.name + "_",
                extension="grid",
                dir=Directory.objects.get(name="Grids", project_id=project.id)
            )
            _file_info.save()
            _grid = Grid(
                topLeftCoordinate=[p1_x, p1_y],
                bottomRightCoordinate=[p2_x, p2_y],
                ortophoto=_ortophoto,
                cell_size=CELL_SIZE,
                file_info=_file_info
            )
            _grid.save()
            # change the name on the file info
            _file_info.name += str(_grid.id)
            _file_info.save()

            utils.cell_cutter(ortophoto_path, row, column, p1_x, p1_y, p2_x, p2_y, _grid.id)

        # Manual classification of a tile on the grid
        # TODO: ADD DRAG BRUSH FEATURE
        print(manual_classifier_form.errors)
        if manual_classifier_form.is_valid():
            print("valid")
            try:
                _grid = Grid.objects.get(file_info_id=manual_classifier_form.cleaned_data['grid'])
                _ortophoto = Ortophoto.objects.get(grid=_grid)
            except Grid.DoesNotExist:
                return redirect("/projects")
            except Ortophoto.DoesNotExist:
                return redirect("/projects")

            # get the brush path pixels
            brush_json = json.loads(response.POST['point'])
            brush = np.array(brush_json)
            brush_path = brush.astype(np.int)

            # calculate real pixel-position of the point
            img_width, img_height = manual_classifier_form.cleaned_data['classification_image_size'].split(", ")
            # p_x, p_y = brush_path[0]

            img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _ortophoto.thumbnail.name)))
            real_height, real_width = img.shape[:2]

            # factor is the multiplication factor between the dimensions in the frontend and the image's real dimensions
            # multiplied by 10 because the map is compressed 10% to create the png
            x_factor, y_factor = real_width / int(img_width), real_height / int(img_height)
            brush_path = [(math.floor(int(p[0]) * x_factor) * 10, math.floor(int(p[1]) * y_factor) * 10) for p in brush_path ]

            # get top left in meters
            top_left_pixels = _grid.topLeftCoordinate
            bottom_right_pixels = _grid.bottomRightCoordinate
            ortophoto_path = os.path.join(MEDIA_ROOT, _grid.ortophoto.content.name)
            top_left_meters = utils.ortophoto_transformation_pixel_to_coordinate(
                ortophoto_path, top_left_pixels[0], top_left_pixels[1]
            )

            # point = (math.floor(int(p_x) * x_factor) * 10, math.floor(int(p_y) * y_factor) * 10)
            classification = manual_classifier_form.cleaned_data['classification_index']
            brush_size = manual_classifier_form.cleaned_data['brush_size'] - 1
            for point in brush_path:

                # check if point is inside the grid
                if point[0] < top_left_pixels[0] or point[0] > bottom_right_pixels[0]:
                    print("invalid x")
                    return redirect("/projects/" + str(project_id) + "/vegetation")

                if point[1] < top_left_pixels[1] or point[1] > bottom_right_pixels[1]:
                    print("invalid y")
                    return redirect("/projects/" + str(project_id) + "/vegetation")

                # compute the offset of the point to the top left
                point_meters = utils.ortophoto_transformation_pixel_to_coordinate(ortophoto_path, point[0], point[1])
                diff = [round(point_meters[0]-top_left_meters[0]), round(top_left_meters[1]-point_meters[1])]
                # print('offset:', diff)

                # get column and row of point in grid
                cell_size = _grid.cell_size
                column = diff[0] // cell_size
                row = diff[1] // cell_size

                # get the affected tiles
                column_range = [math.floor(column - brush_size/2), math.floor(column + brush_size/2)]
                row_range = [math.floor(row - brush_size/2), math.floor(row + brush_size/2)]

                affected_tiles = Tile.objects.all().filter(grid=_grid)\
                    .filter(position__0__range=column_range)\
                    .filter(position__1__range=row_range)\
                    .filter(~Q(classification=classification))


                # change the classification of each tile
                # print("cleaning tiles")
                with concurrent.futures.ThreadPoolExecutor(max_workers=max(row, column)) as executor:
                    future_mask = {
                        executor.submit(utils.change_classification, tile, classification): tile.id
                        for tile in affected_tiles
                    }

                    done, _ = concurrent.futures.wait(future_mask, timeout=20, return_when=concurrent.futures.ALL_COMPLETED)

            return redirect("/projects/" + str(project_id) + "/vegetation?grid=" +
                            str(manual_classifier_form.cleaned_data['grid'])
                            + '&selected=' + str(classification) + "&brush=" + str(brush_size+1))

    return redirect("/projects/" + str(project_id) + "/vegetation")


def auto_classifier(request, project_id, grid_id):
    try:
        project = Project.objects.get(id=project_id)
        grid = Grid.objects.get(id=grid_id, ortophoto__file_info__dir__project_id=project_id)
    except Project.DoesNotExist:
        return redirect("/projects")
    except Grid.DoesNotExist:
        return redirect("/projects")

    if request.method == "GET":
        tile_list = Tile.objects.all().filter(grid_id=grid.id)
        classified_tiles = tile_list.filter(classification__isnull=False)

        if len(classified_tiles) == 0:
            # TODO raise error if no classification exists
            means = [[233, 231, 234], [140, 138, 107], [114, 114, 98], [60, 63, 31]]
        else:
            classification_total = Classification.objects.all().filter(model=grid.model)
            print(classification_total)

            means = []
            for c in classification_total:
                pixel_avg = utils.simplified_pixel_average(tile_list.filter(classification=c.classificationIndex))
                if pixel_avg:
                    means.append(pixel_avg)
            print(means)

        # # if we use distance, this block is unnecessary #
        # lab_means = []
        # lab_colors = []
        #
        # for mean in means:
        #     lab_means.append(sRGBColor(mean[0], mean[1], mean[2]))
        #
        # # Convert from RGB to Lab Color Space
        # lab_colors.append(convert_color(lab_means[0], LabColor))
        # # Convert from RGB to Lab Color Space
        # lab_colors.append(convert_color(lab_means[1], LabColor))
        # # Convert from RGB to Lab Color Space
        # lab_colors.append(convert_color(lab_means[2], LabColor))
        # # Convert from RGB to Lab Color Space
        # lab_colors.append(convert_color(lab_means[3], LabColor))
        # # end of block #

        for tile in tile_list:
            # tile.classification = utils.visually_closest(tile, lab_colors)
            tile.classification = utils.numerically_closest(tile, means)
            tile.save()

    return redirect("/projects/" + str(project.id) + "/vegetation?grid=" + str(grid.file_info.id))


def export_fuel_map(request, project_id, grid_id):
    try:
        project = Project.objects.get(id=project_id)
        grid = Grid.objects.get(id=grid_id, ortophoto__file_info__dir__project_id=project_id)
    except Project.DoesNotExist:
        return redirect("/projects")
    except Grid.DoesNotExist:
        return redirect("/projects")

    if request.method == 'GET':
        print("store to fuel map")

        # CELL_SIZE - na bd
        cell_size = grid.cell_size

        # bottom left coord -  pontos na bd em pixels
        _top_left = grid.topLeftCoordinate
        _bottom_right = grid.bottomRightCoordinate

        bottom_left_pixels = [_top_left[0], _bottom_right[1]]
        top_right_pixels = [_bottom_right[0], _top_left[1]]

        ortophoto_path = os.path.join(MEDIA_ROOT, grid.ortophoto.content.name)
        x_bottom_left_meters, y_bottom_left_meters = utils.ortophoto_transformation_pixel_to_coordinate(
            ortophoto_path, bottom_left_pixels[0], bottom_left_pixels[1]
        )
        print(x_bottom_left_meters, y_bottom_left_meters)
        x_bottom_left_meters = round(x_bottom_left_meters)
        y_bottom_left_meters = round(y_bottom_left_meters)

        # calcular cols e rows
        x_top_right_meters, y_top_right_meters = utils.ortophoto_transformation_pixel_to_coordinate(
            ortophoto_path, top_right_pixels[0], top_right_pixels[1]
        )
        diff_x, diff_y = abs(x_top_right_meters - x_bottom_left_meters), abs(y_bottom_left_meters - y_top_right_meters)

        column = int(abs(diff_x // cell_size))
        row = int(abs(diff_y // cell_size))

        # tile list da bd
        file_output = str(column) + '\n' + \
            str(row) + '\n' + \
            str(x_bottom_left_meters) + '\n' + \
            str(y_bottom_left_meters) + '\n' + \
            str(cell_size) + '\n'

        tile_list = Tile.objects.all().filter(grid_id=grid.id)
        print(tile_list.filter(position=[0, 0]))
        model = grid.model
        formatted_str = '{:02.1f}'
        tiles_str = ""
        for r in range(row):
            for c in range(column):
                elem = tile_list.filter(position=[c, r]).first()
                # TODO: exception when has no classification
                elem_percentage = float(Classification.objects.all().filter(model=model, classificationIndex=elem.classification).first().minPercentage)
                if elem_percentage == 0:
                    elem_percentage = 99.0
                tiles_str += formatted_str.format(elem_percentage) + ' '
            tiles_str += "\n"

        file_output += tiles_str

        filename = 'fuelmap_' + grid.ortophoto.file_info.name + '.asc'
        response = HttpResponse(file_output, content_type='application/octet-stream')
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        return response

    return redirect("/projects/" + str(project.id) + "/vegetation?id=" + str(grid.ortophoto.file_info.id))


def upload_orthphoto(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return redirect("/projects")

    if request.method == "POST":
        ortophoto_form = UploadOrtophoto(request.POST, request.FILES)
        if ortophoto_form.is_valid():
            name, extension = request.FILES['image'].name.split('.')
            start = time.time()

            try:
                # file already exists in the server
                FileInfo.objects.get(name=name, extension=extension, dir__project__id=project.id)
                return HttpResponse("There is a file with that name already")

            except FileInfo.DoesNotExist:
                # create file info
                _file_info = FileInfo(
                    name=name,
                    extension=extension,
                    dir=Directory.objects.get(name="Ortophotos", project_id=project.id)
                )
                _file_info.save()
                _image = Ortophoto(
                    file_info=_file_info,
                    content=request.FILES['image'],
                )
                _image.save()

                ortophoto = gdal.Open(os.path.abspath(os.path.join(MEDIA_ROOT, _image.content.name)))
                print("Number of channels:", ortophoto.RasterCount)  # 4

                options_list = [
                    '-co COMPRESS=JPEG',
                    '-co TILED=YES',
                ]
                options_string = " ".join(options_list)
                gdal.Translate(
                    os.path.abspath(os.path.join(MEDIA_ROOT, "ortophotos/{}_compressed.{}".format(name, extension))),
                    ortophoto,
                    options=options_string)

                file = File(open(os.path.abspath(os.path.join(MEDIA_ROOT,
                                                              "ortophotos/{}_compressed.{}".format(name, extension))),
                                 "rb"))
                _image.content.delete()
                _image.content.save("{}.{}".format(name, extension), file)
                os.remove(
                    os.path.abspath(os.path.join(MEDIA_ROOT, "ortophotos/{}_compressed.{}".format(name, extension))))

                print("Uploaded tiff ortophoto {}.{}".format(name, extension))
                print("Ellapsed time: {}s".format(time.time() - start))
                return redirect("/projects/" + str(project_id) + "/vegetation")

    else:
        ortophoto_form = UploadOrtophoto()

    param = {
        'project': project,
        'project_dirs': Directory.objects.all().filter(project_id=project.id),
        'project_files': FileInfo.objects.all().filter(dir__project_id=project.id),
        'ortophoto_form': ortophoto_form
    }
    return render(request, "main/vegetation_characterization.html", param)


def frontpage(response):
    return render(response, "main/front_page.html", {})


def upload(request, project_id):
    if not request.user.is_authenticated:
        return redirect("/login")

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return redirect("/projects")

    if request.method == 'POST':
        form = UploadImage(request.POST, request.FILES)
        if form.is_valid():
            name, extension = request.FILES['image'].name.split('.')
            print(request.FILES)
            print(name, extension)

            try:
                # file already exists in the server
                FileInfo.objects.get(name=name, extension=extension, dir__project__id=project.id)
                return HttpResponse("There is a file with that name already")

            except FileInfo.DoesNotExist:
                # create file info
                _file_info = FileInfo(
                    name=name,
                    extension=extension,
                    dir=Directory.objects.get(name="Images", project_id=project.id)
                )
                _file_info.save()
                _image = ImageFrame(
                    file_info=_file_info,
                    content=request.FILES['image'],
                )
                _image.save()

            img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _image.content.name)))

            # create empty mask of image's size ans "serialize" it
            _mask = np.zeros(img.shape[:2], np.uint8)
            mask_encoded = pickle.dumps(_mask)
            # save mask in the previously created image
            _image.mask = mask_encoded
            _image.save()

    return redirect("/projects/" + str(project_id) + "/segmentation")


def upload_video(request, project_id):
    if not request.user.is_authenticated:
        return redirect("/login")

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return redirect("/projects")

    if request.method == 'POST':
        form = UploadVideo(request.POST, request.FILES)
        print(form.errors)
        if form.is_valid():
            name, extension = request.FILES['video'].name.split('.')
            frame_number = request.POST['frames']
            originTimestamp = request.POST['videoOriginDateTime']
            startingTimestamp = request.POST['startingDateTime']

            video = Video(
                frame_number=frame_number,
                name=name,
                extension=extension,
                content=request.FILES['video']
            )
            video.save()

            video_capture = cv2.VideoCapture()
            video_capture.open(os.path.abspath(os.path.join(MEDIA_ROOT, video.content.name)))
            max_frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
            fps = video_capture.get(cv2.CAP_PROP_FPS)
            print("Successfully loaded {}.{} with {} frames".format(video.name, video.extension, max_frames))

            startingDateTime = datetime.strptime(startingTimestamp, "%Y-%m-%d %H:%M:%S")
            originDateTime = datetime.strptime(originTimestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            skipSeconds = (startingDateTime - originDateTime).seconds
            skipFrames = int(skipSeconds * fps)
            print('seconds to skip:', skipSeconds, '-> frames to skip:', skipFrames)

            fpm = fps * 60
            step = int(fpm / int(frame_number))
            print('capturing in a step of', step)

            # step = math.floor(max_frames / int(frame_number))
            cur_frame = 1
            frame_index = 1  # retrieved frame index

            frames_dir = Directory(
                name=name,
                project=project,
                parent=Directory.objects.get(project__id=project.id, name="Frames")
            )
            frames_dir.save()
            temp = skipFrames
            try:
                while video_capture.isOpened() and cur_frame < max_frames - temp:
                    _, frame = video_capture.read()  # read next image from video
                    if skipFrames > 0:
                        skipFrames -= 1
                    else:
                        if cur_frame % step == 0:
                            frame_name = "{}_{}".format(name, frame_index)
                            timestamp = (cur_frame + temp) / fps
                            print("Captured frame at second", timestamp, "(" + str(originDateTime + timedelta(seconds=timestamp)) + ")")

                            _, frame_arr = cv2.imencode('.png', frame)  # Numpy one-dim array representative of the img
                            frame_bytes = frame_arr.tobytes()
                            _frame = ImageFile(io.BytesIO(frame_bytes), name='{}.png'.format(frame_name))

                            _file_info = FileInfo(
                                name=frame_name,
                                extension='png',
                                dir=frames_dir
                            )
                            _file_info.save()

                            _frame = ImageFrame(
                                video=video,
                                file_info=_file_info,
                                content=_frame,
                                timestamp=timestamp,
                            )
                            _frame.save()

                            # create empty mask of image's size ans "serialize" it
                            _mask = np.zeros(frame.shape[:2], np.uint8)
                            mask_encoded = pickle.dumps(_mask)
                            # save mask in the previously created image
                            _frame.mask = mask_encoded
                            _frame.save()

                            frame_index += 1
                        cur_frame += 1
            finally:
                video_capture.release()
                # delete content from model and from file system
                video.content.delete()
                print(video.content)
                print("Done")

    return redirect("/projects/" + str(project_id) + "/segmentation")


def segmentation(response, project_id):
    if not response.user.is_authenticated:
        return redirect("/login")

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return redirect("/projects")

    if response.method == "GET":
        image = None
        if 'id' in response.GET:
            try:
                image = ImageFrame.objects.get(file_info__id=response.GET['id'])
            except ImageFrame.DoesNotExist:
                image = None

        param = {
            'image': image,
            'project': project,
            'project_dirs': Directory.objects.all().filter(project_id=project.id),
            'project_files': FileInfo.objects.all().filter(dir__project_id=project.id),
            'image_form': UploadImage(),
            'video_form': UploadVideo(),
            'segmentation': Segmentation(),
        }

        if image and image.video:
            param['video_frames'] = ImageFrame.objects.all().filter(
                video_id=image.video.id,
                file_info__dir__project_id=project_id
            )

        # if the image_id is valid check if it has a mask
        if image is None or image.mask is None:
            return render(response, "main/fire_segmentation.html", param)

        img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, image.content.name)))
        mask = pickle.loads(image.mask)

        mask_is_new = (mask == 0).all()
        if mask_is_new:
            return render(response, "main/fire_segmentation.html", param)

        # "serialize" the updated mask
        mask_encoded = pickle.dumps(mask)
        # update the mask file on db
        image.mask = mask_encoded
        image.save()

        mask_32S = mask.astype(
            np.int32)  # used to convert the mask to CV_32SC1 so it can be accepted by cv2.watershed()
        blurred = cv2.blur(img, (2, 2))
        cv2.watershed(blurred, mask_32S)

        # genOverlay()
        _m = np.uint8(mask_32S)
        m = cv2.cvtColor(_m, cv2.COLOR_GRAY2BGR)
        segmented = cv2.addWeighted(img, 0.5, m, 0.5, 0, dtype=cv2.CV_8UC3)

        # convert masked image to base64
        segmented_base64 = utils.opencv_to_base64(segmented, image.file_info.extension)
        param['segmented'] = 'data:image/jpg;base64,{image}'.format(image=segmented_base64.decode())

        return render(response, "main/fire_segmentation.html", param)

    elif response.method == "POST":
        param = {
            'image': None,
            'project': project,
            'project_dirs': Directory.objects.all().filter(project_id=project.id),
            'project_files': FileInfo.objects.all().filter(dir__project_id=project.id),
            'image_form': UploadImage(),
            'video_form': UploadVideo(),
            'segmentation': Segmentation(initial={"pen": False, "eraser": False}),
        }

        if 'image_id' not in response.POST or response.POST['image_id'] == '':
            return redirect(response.build_absolute_uri())

        mode = None
        if 'pen' in response.POST:
            param['segmentation'] = Segmentation(initial={"pen": True})
            mode = True

        if 'eraser' in response.POST:
            param['segmentation'] = Segmentation(initial={"eraser": True})
            mode = False

        # check if image exists
        _id = response.POST['image_id']
        try:
            _image = ImageFrame.objects.get(file_info__id=_id)
            _image_file = _image.file_info
            param['image'] = _image
            if _image.video:
                param['video_frames'] = ImageFrame.objects.all().filter(video_id=_image.video.id,
                                                                        file_info__dir__project_id=project_id),

        except ImageFrame.DoesNotExist:
            return render(response, "main/fire_segmentation.html", param)

        if 'path' not in response.POST:
            return render(response, "main/fire_segmentation.html", param)

        # compute the path from the coordinates
        path_json = json.loads(response.POST['path'])
        path = np.array(path_json)
        mouse_path = path.astype(np.int)

        # if the image_id is valid check if it has a mask
        if _image is None or _image.mask is None:
            return render(response, "main/fire_segmentation.html", param)

        img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _image.content.name)))
        mask = pickle.loads(_image.mask)

        # Segmenter_main.cpp implementation ########
        # drawMask(): adds clicked points as interest points to the image mask
        for point in mouse_path:
            if mode is True:
                mask[point[1], point[0]] = 255
            else:
                mask[point[1], point[0]] = 1

        # "serialize" the updated mask
        mask_encoded = pickle.dumps(mask)
        # update the mask file on db
        _image.mask = mask_encoded
        _image.save()

        mask_32S = mask.astype(
            np.int32)  # used to convert the mask to CV_32SC1 so it can be accepted by cv2.watershed()
        blurred = cv2.blur(img, (2, 2))
        cv2.watershed(blurred, mask_32S)

        # genOverlay()
        _m = np.uint8(mask_32S)
        m = cv2.cvtColor(_m, cv2.COLOR_GRAY2BGR)
        segmented = cv2.addWeighted(img, 0.5, m, 0.5, 0, dtype=cv2.CV_8UC3)

        # convert masked image to base64
        segmented_base64 = utils.opencv_to_base64(segmented, _image.file_info.extension)
        param['segmented'] = 'data:image/jpg;base64,{image}'.format(image=segmented_base64.decode())

        return render(response, "main/fire_segmentation.html", param)


def generate_contour(request, file_id, project_id):
    if not request.user.is_authenticated:
        return redirect("/login")

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return redirect("/projects")

    try:
        _image = ImageFrame.objects.get(file_info_id=file_id)
    except ImageFrame.DoesNotExist:
        return redirect(request.get_full_path())

    img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _image.content.name)))
    mask = pickle.loads(_image.mask)

    # create the final shape
    mask_32S = mask.astype(np.int32)  # used to convert the mask to CV_32SC1 so it can be accepted by cv2.watershed()
    blurred = cv2.blur(img, (2, 2))
    cv2.watershed(blurred, mask_32S)

    # convert shape to polygon
    binary = np.float32(mask_32S)  # convert mask to CV_32FC1
    _, binary = cv2.threshold(binary, 200, 255, cv2.THRESH_BINARY)
    binary = binary.astype(np.uint8)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    binary = cv2.dilate(binary, kernel)
    binary = cv2.erode(binary, kernel)

    vertexes, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if len(vertexes) > 1:
        print("More than one polygon were identified")
        # TODO: add return_bigger to Segmentation form and input on pop up
        # if 'return_bigger' in request.GET and request.GET['return_bigger'] == "1":
        sizes = [len(pol) for pol in vertexes]
        vertexes = vertexes[sizes.index(max(sizes))]
    # else:
    # return redirect("/segmentation?id=" + str(file_id)) + "&error=TooManyValues
    else:
        vertexes = vertexes[0]

    # cv2.drawContours(img, vertexes, -1, (0, 255, 0), 3)
    # cv2.imshow("Contours", img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # fs_wkt = ""
    # for point in vertexes:
    #     fs_wkt += ", " + str(point[0][0]) + " " + str(point[0][1])
    # fs_wkt = "POLYGON ((" + fs_wkt[2:] + ", " + str(vertexes[0][0][0]) + " " + str(vertexes[0][0][1]) + "))\n"
    # print(fs_wkt)

    # store polygon on db
    wkt_list = []
    for point in vertexes:
        wkt_list.append((point[0][0], point[0][1]))
    wkt_list.append((vertexes[0][0][0], vertexes[0][0][1]))
    wkt = tuple(wkt_list)

    polygon = Polygon(LinearRing(wkt))
    print(polygon)
    _image.polygon = polygon
    _image.save()

    return redirect('/projects/' + str(project.id) + '/segmentation?id=' + str(file_id))


# TODO: Fire Progression Animation and Processing
"""
    GEOREFERENCING
"""


def progression(request, project_id):
    if not request.user.is_authenticated:
        return redirect("/login")

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return redirect("/projects")

    if request.method == "GET":
        frame = None
        if 'id' in request.GET:
            try:
                frame = ImageFrame.objects.get(file_info_id=request.GET['id'])
            except ImageFrame.DoesNotExist:
                frame = None

        param = {
            'frame': frame,
            'project': project,
            'project_dirs': Directory.objects.all().filter(project_id=project.id),
            'project_files': FileInfo.objects.all().filter(dir__project_id=project.id),
            'file_form': UploadCoordFile(),
            'georreferencing': Georreferencing(),
        }

        # if the frame_id is valid check if it has been georreferenced
        if frame is None or frame.polygon is None:
            return render(request, "main/fire_progression.html", param)

        img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, frame.content.name)))
        # georreference = pickle.loads(frame.polygon)
        georreference = frame.polygon.wkt
        print(georreference)

        param['georreferenced'] = georreference

        return render(request, "main/fire_progression.html", param)

    elif request.method == 'POST':
        param = {
            'frame': None,
            'project': project,
            'project_dirs': Directory.objects.all().filter(project_id=project.id),
            'project_files': FileInfo.objects.all().filter(dir__project_id=project.id),
            # 'file_form': UploadCoordFile(),
            'georreferencing': Georreferencing(initial={"marker": False}),
        }

        if 'frame_id' not in request.POST or request.POST['frame_id'] == '':
            return redirect(request.build_absolute_uri())

        mode = None
        if 'marker' in request.POST:
            param['georreferencing'] = Georreferencing(initial={'marker': True})
            mode = True

        # check if frame exists
        _id = int(request.POST['frame_id'])
        try:
            _frame = ImageFrame.objects.get(file_info_id=_id)
            _frame_file = _frame.file_info
            param['frame'] = _frame
        except ImageFrame.DoesNotExist:
            return render(request, 'main/fire_progression.html', param)

        if 'pixels' not in request.POST or 'geo' not in request.POST:
            return render(request, "main/fire_progression.html", param)

        # compute the pairs from the coordinates
        pixels_json = json.loads(request.POST['pixels'])
        print(pixels_json)
        geo_json = json.loads(request.POST['geo'])
        print(geo_json)

        # if the frame_id is valid check if it has been georreferenced
        if _frame is None or _frame.polygon is None:
            return render(request, "main/fire_segmentation.html", param)

        img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _frame.content.name)))

        # TODO: Georeference points
        pts_src = np.array(pixels_json)
        pts_dst = np.array(geo_json).astype(int)
        print(pts_dst)

        # given reference points from 2 spaces, returns a matrix that can convert between the 2 spaces (in this case, pixel to geo coords)
        h, status = cv2.findHomography(pts_src, pts_dst)

        coords = _frame.polygon.wkt.split("((")[1].split("))")[0].split(",")

        geo_coords = ""
        wkt_str = ""
        for coord in coords:
            coord_split = coord.strip().split(" ")
            point_homogenous = h.dot([float(coord_split[0]), float(coord_split[1]), 1])
            if len(point_homogenous) != 3:
                geo_coord = [0, 0]
            else:
                z = point_homogenous[2]
                geo_coord = [point_homogenous[0] / z, point_homogenous[1] / z]
            geo_coords = geo_coords + str(geo_coord[0]) + " " + str(geo_coord[1]) + ", "
            geo_coords = geo_coords[:-2]
            wkt_str = "POLYGON ((" + geo_coords + "))"
        print(wkt_str)
        # TODO save georef polygon

        # Converted polygon WKT, to be analyzed by JS
        param['georreferenced'] = wkt_str
    return render(request, "main/fire_progression.html", param)


# TODO: Animate Polygons
'''
def generate_georreference(request, file_id, project_id):
    if not request.user.is_authenticated:
    return redirect("/login")

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return redirect("/projects")

    try:
        _frame = ImageFrame.objects.get(file_info_id=file_id)
    except ImageFrame.DoesNotExist:
        return redirect(request.get_full_path())


    img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _frame.content.name)))
    polygon = pickle.loads(_frame.polygon)
    georeference = pickle.loads(_frame.georeference)


    return redirect('/projects/' + str(project_id) + '/progression?id=' + str(file_id))
'''


# DISPERFIRE FILE EXPORT VIEW
def export_disperfire_file(request, project_id, video_id, grid_id):
    if not request.user.is_authenticated:
        return redirect("/login")

    try:
        _project = Project.objects.get(id=project_id)
        _grid = Grid.objects.get(id=grid_id, ortophoto__file_info__dir__project_id=project_id)
        _video = Video.objects.get(id=video_id)
    except Project.DoesNotExist:
        print("no porject")
        return redirect("/projects")
    except Grid.DoesNotExist:
        print("no grid")
        return redirect("/projects")
    except Video.DoesNotExist:
        print("no video")
        return redirect("/projects")

    # add test polygon
    coords = ((-7.614775, 41.391031), (-7.614078, 41.390717), (-7.615237, 41.390556), (-7.614775, 41.391031))
    poly = Polygon(coords)

    frame = ImageFrame.objects.get(id=21)
    frame.geoRefPolygon = poly
    frame.save()

    coords = ((-7.615859, 41.391369), (-7.615437, 41.388883), (-7.612594, 41.388883), (-7.613800, 41.391282), (-7.615859, 41.391369))
    poly = Polygon(coords)
    frame = ImageFrame.objects.get(id=22)
    frame.geoRefPolygon = poly
    frame.save()


    # get top left in meters
    cell_size = _grid.cell_size
    top_left_pixels = _grid.topLeftCoordinate
    ortophoto_path = os.path.join(MEDIA_ROOT, _grid.ortophoto.content.name)
    top_left_meters = utils.ortophoto_transformation_pixel_to_coordinate(
        ortophoto_path, top_left_pixels[0], top_left_pixels[1]
    )

    frame_list = ImageFrame.objects.all().filter(video_id=_video.id).order_by('id')
    print(frame_list)

    for i in range(0, len(frame_list)):
        print("frame", i)
        cur_frame = frame_list[i]

        # get outer bounds of bigger polygon
        envelope = cur_frame.geoRefPolygon.envelope
        print('envelope', envelope)
        coords = envelope.coords[0][:-1]

        x_coords = [x[0] for x in coords]
        max_x, min_x = max(x_coords), min(x_coords)
        y_coords = [y[1] for y in coords]
        max_y, min_y = max(y_coords), min(y_coords)

        min_point = (min_x, min_y)
        max_point = (max_x, max_y)
        min_point_meters = utils.ortophoto_transform_degrees_to_meters(ortophoto_path, min_point[0], min_point[1])
        max_point_meters = utils.ortophoto_transform_degrees_to_meters(ortophoto_path, max_point[0], max_point[1])

        max_dif = [abs(top_left_meters[0] - max_point_meters[0]), abs(top_left_meters[1] - max_point_meters[1])]
        max_col, max_row = int(max_dif[0] // cell_size) + 1, int(max_dif[1] // cell_size) + 1
        min_dif = [abs(top_left_meters[0] - min_point_meters[0]), abs(top_left_meters[1] - min_point_meters[1])]
        min_col, min_row = int(min_dif[0] // cell_size), int(min_dif[1] // cell_size)

        if min_col > max_col:
            temp = min_col
            min_col = max_col
            max_col = temp

        if min_row > max_row:
            temp = min_row
            min_row = max_row
            max_row = temp

        tiles_to_analyse = Tile.objects.all().filter(grid=_grid, start_time_frame__isnull=True)\
            .filter(position__0__range=[min_col, max_col-1])\
            .filter(position__1__range=[min_row, max_row-1])
        print(len(tiles_to_analyse))
        print('total', len(Tile.objects.all().filter(grid=_grid)))

        for tile in tiles_to_analyse:

            # calculate vertices in meters
            temp = ((tile.position[0]*cell_size + top_left_meters[0]), (top_left_meters[1] - tile.position[1]*cell_size))
            tile_vertices = [temp,
                             (temp[0] + cell_size, temp[1]),
                             (temp[0] + cell_size, temp[1] - cell_size),
                             (temp[0], temp[1] - cell_size)]

            # convert 4 vertices to degrees
            tile_vertices_degrees = [utils.ortophoto_transform_meters_to_degrees(ortophoto_path, x[0], x[1]) for x in tile_vertices]
            tile_vertices_degrees.append(tile_vertices_degrees[0])
            tile_vertices_degrees = tuple(tile_vertices_degrees)

            # create polygon and intersect with burnt geo-referenced polygon
            tile_polygon = Polygon(tile_vertices_degrees)
            intersectTile = cur_frame.geoRefPolygon.intersects(tile_polygon)

            # update tile's start time frame
            if intersectTile:
                tile.start_time_frame = cur_frame
                tile.save()

    # WRITE FILE TO SEND TO CLIENT
    # calculate columns and rows
    bottom_right = _grid.bottomRightCoordinate
    bottom_right_meters = utils.ortophoto_transformation_pixel_to_coordinate(
        ortophoto_path, bottom_right[0], bottom_right[1]
    )
    diff_x, diff_y = abs(top_left_meters[0] - bottom_right_meters[0]), abs(top_left_meters[1] - bottom_right_meters[1])
    column = int(abs(diff_x // cell_size))
    row = int(abs(diff_y // cell_size))


    video_frames = ImageFrame.objects.all().filter(video_id=_video.id)
    min_timestamp, max_timestamp = video_frames.aggregate(Min('timestamp'))['timestamp__min'], video_frames.aggregate(Max('timestamp'))['timestamp__max']
    print(min_timestamp, max_timestamp)

    file_output = str(round(max_timestamp)) + '\n' + str(round(min_timestamp)) + '\n'

    tile_list = Tile.objects.all().filter(grid_id=_grid.id)
    tiles_str = ""
    for r in range(row):
        for c in range(column):
            elem = tile_list.filter(position=[c, r]).first()

            if elem.start_time_frame is not None:
                elem_timestamp = round(elem.start_time_frame.timestamp)
                tiles_str += str(elem_timestamp) + ' '

            else:
                tiles_str += '-1 '
        tiles_str += "\n"

    file_output += tiles_str

    filename = 'disperModel_' + _grid.ortophoto.file_info.name + '.asc'
    response = HttpResponse(file_output, content_type='application/octet-stream')
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response
