import io
import json
import math
import pickle
import time

from django.core.files import File
from django.core.files.images import ImageFile
from django.shortcuts import render, redirect
from django.contrib.gis.geos import Polygon, LinearRing
from django.db.models import Q
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color

from FIRELab_website.settings import MEDIA_ROOT
from main import utils
from main.forms import *
import cv2
import os
import numpy as np
from django.http import HttpResponse
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
		param = {
			'project': project,
			'project_dirs': Directory.objects.all().filter(project_id=project.id),
			'project_files': FileInfo.objects.all().filter(dir__project_id=project.id),
			'ortophoto_form': ortophoto_form,
			'grid_draw': grid_draw_form
		}

		if 'id' in response.GET:
			try:
				_ortophoto = Ortophoto.objects.get(file_info_id=response.GET['id'])
			except Ortophoto.DoesNotExist:
				return redirect("/projects/" + str(project_id) + "/vegetation")

			if _ortophoto.thumbnail:
				print("Image exists")
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

			# verify if grid exists
			try:
				_grid = Grid.objects.get(ortophoto=_ortophoto)
				param['grid'] = _grid
			except Grid.DoesNotExist:
				return render(response, "main/vegetation_characterization.html", param)

			# DRAW GRID HERE #
			_top_left = _grid.topLeftCoordinate
			_bottom_right = _grid.bottomRightCoordinate

			print("Corner pixels in ortophoto:", _top_left, _bottom_right)

			top_left = [int(e * 0.10) for e in _top_left]
			bottom_right = [int(e * 0.10) for e in _bottom_right]

			print("Corner pixels in thumbnail:", top_left, bottom_right)

			img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _ortophoto.thumbnail.name)))
			tiles = Tile.objects.all().filter(grid_id=_grid.id)
			x_pos = max([t.position[0] for t in tiles])

			cell_size = int((bottom_right[0] - top_left[0]) / (x_pos + 1))

			gridded_image = utils.draw_grid(img, cell_size, top_left, bottom_right)
			gridded_image[np.where((gridded_image == [0, 0, 0]).all(axis=2))] = [255, 255, 255]
			# TODO: maybe store gridded_image in db

			gridded_image_base64 = utils.opencv_to_base64(gridded_image, 'png')
			param['gridded_image'] = 'data:image/png;base64,{image}'.format(image=gridded_image_base64.decode())

			# DRAW IMAGE WITH JUST THE WANTED FILTERS
			if 'none' in response.GET and response.GET['none'] == "0":
				print("removing level 0")
				tiles = tiles.filter(~Q(classification=0))
			if 'low' in response.GET and response.GET['low'] == "0":
				print("removing level 1")
				tiles = tiles.filter(~Q(classification=1))
			if 'medium' in response.GET and response.GET['medium'] == "0":
				print("removing level 2")
				tiles = tiles.filter(~Q(classification=2))
			if 'high' in response.GET and response.GET['high'] == "0":
				print("removing level 3")
				tiles = tiles.filter(~Q(classification=3))

			to_classify = gridded_image[top_left[1]:bottom_right[1], top_left[0]: bottom_right[0]]
			mask = np.zeros(to_classify.shape[:2], np.uint8)
			mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

			for tile in tiles:
				test_tile = tile.position
				start_point = (test_tile[0] * cell_size, test_tile[1] * cell_size)
				end_point = (start_point[0] + cell_size, start_point[1] + cell_size)

				if tile.classification == 0:
					mask = cv2.rectangle(mask, start_point, end_point, (20, 20, 255), -1)
				elif tile.classification == 1:
					mask = cv2.rectangle(mask, start_point, end_point, (122, 209, 240), -1)
				elif tile.classification == 2:
					mask = cv2.rectangle(mask, start_point, end_point, (150, 240, 100), -1)
				elif tile.classification == 3:
					mask = cv2.rectangle(mask, start_point, end_point, (45, 80, 20), -1)

			classified_img = cv2.addWeighted(to_classify, 0.5, mask, 0.5, 0, dtype=cv2.CV_8UC3)
			gridded_image[top_left[1]:bottom_right[1], top_left[0]: bottom_right[0]] = classified_img

			gridded_image_base64 = utils.opencv_to_base64(gridded_image, 'png')
			param['gridded_image'] = 'data:image/png;base64,{image}'.format(image=gridded_image_base64.decode())

		return render(response, "main/vegetation_characterization.html", param)

	else:
		grid_draw_form = DrawGridForm(response.POST)
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

			CELL_SIZE = 5  # in meters
			patch_x = diff_x % CELL_SIZE  # value to remove to lat2
			x2_m -= patch_x

			patch_y = diff_y % CELL_SIZE
			y2_m -= patch_y

			p2_x, p2_y = utils.ortophoto_transformation_coordinate_to_pixel(ortophoto_path, x2_m, y2_m)

			column = int(abs(diff_x // CELL_SIZE))
			row = int(abs(diff_y // CELL_SIZE))

			_grid = Grid(
				topLeftCoordinate=[p1_x, p1_y],
				bottomRightCoordinate=[p2_x, p2_y],
				ortophoto=_ortophoto,
				cell_size=CELL_SIZE
			)
			_grid.save()

			utils.cell_cutter(ortophoto_path, row, column, p1_x, p1_y, p2_x, p2_y, _grid.id)

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
		# TODO: do means using tiles in db
		tile_list = Tile.objects.all().filter(grid_id=grid.id)

		classified_tiles = tile_list.filter(classification__isnull=False)
		means = [[233, 231, 234], [140, 138, 107], [114, 114, 98], [60, 63, 31]]

		if len(classified_tiles) == 0:
			means = [[233, 231, 234], [140, 138, 107], [114, 114, 98], [60, 63, 31]]
		else:
			level_0_tiles = tile_list.filter(classification=0)
			level_1_tiles = tile_list.filter(classification=1)
			level_2_tiles = tile_list.filter(classification=2)
			level_3_tiles = tile_list.filter(classification=3)

			avg_0 = utils.simplified_pixel_average(level_0_tiles)
			avg_1 = utils.simplified_pixel_average(level_1_tiles)
			avg_2 = utils.simplified_pixel_average(level_2_tiles)
			avg_3 = utils.simplified_pixel_average(level_3_tiles)

			means = [avg_0, avg_1, avg_2, avg_3]

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
		if form.is_valid():
			name, extension = request.FILES['video'].name.split('.')
			frame_number = request.POST['frames']
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
			print("Successfully loaded {}.{} with {} frames".format(video.name, video.extension, max_frames))

			step = math.floor(max_frames / int(frame_number))
			cur_frame = 0
			frame_index = 1  # retrieved frame index

			frames_dir = Directory(
				name=name,
				project=project,
				parent=Directory.objects.get(project__id=project.id, name="Frames")
			)
			frames_dir.save()

			try:
				while video_capture.isOpened() and cur_frame < max_frames:
					_, frame = video_capture.read()  # read next image from video
					if cur_frame % step == 0:
						frame_name = "{}_{}".format(name, frame_index)

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

	# store polygon on db
	wkt_list = []
	for point in vertexes:
		wkt_list.append((point[0][0], point[0][1]))
	wkt_list.append((vertexes[0][0][0], vertexes[0][0][1]))
	wkt = tuple(wkt_list)

	polygon = Polygon(LinearRing(wkt))
	_image.polygon = polygon
	_image.save()

	return redirect('/projects/' + str(project.id) + '/progression?id=' + str(file_id))




"""
	GEOREFERENCING 
"""
def upload_polygon(request, project_id):
	if not request.user.is_authenticated:
		return redirect("/login")
	try:
		project = Project.objects.get(id=project_id)
	except Project.DoesNotExist:
		return redirect("/projects")
	if request.method == 'POST':
		polygon = request.FILES['coords'].read()
		image = ImageFrame.objects.get(file_info__id=request.POST['image_id'])
		image.polygon = polygon
		image.save()


	return redirect("/projects/" + str(project_id) + "/progression?id=" + request.POST['image_id'])

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

		param['georreferenced'] = frame.polygon.wkt[10:-2]

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
		_id = request.POST['frame_id']
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
		geo_json = json.loads(request.POST['geo'])

		# if the frame_id is valid check if it has been georreferenced
		if _frame is None or _frame.polygon is None:
			# print("frame - ", _frame)
			# TODO: Error Message, tell the user the frame needs to be segmented
			return render(request, "main/fire_segmentation.html", param)

		img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _frame.content.name)))

		pts_src = np.array(pixels_json)
		pts_dst = np.array(geo_json)
				
		#given reference points	 from 2 spaces, returns a matrix that can convert between the 2 spaces (in this case, pixel to geo coords)
		h, status = cv2.findHomography(pts_src, pts_dst)

		coords = _frame.polygon.wkt
		coords = coords.split("((")[1].split("))")[0].split(",")

		geo_coord = []
		wkt_str = ""
		for coord in coords:
			coord_split = coord.strip().split(" ")
			point_homogenous = h.dot([float(coord_split[0]), float(coord_split[1]), 1])
			if len(point_homogenous) != 3:
				geo_coord = [0,0]
			else:
				z = point_homogenous[2]
				geo_coord = [point_homogenous[0]/z, point_homogenous[1]/z]

		# store polygon on db
		wkt_list = []
		last = geo_coord[0]
		for point in geo_coord:
			wkt_list.append(point)
		wkt_list.append(last)
		wkt = tuple(wkt_list)

		geo_polygon = Polygon(LinearRing(wkt))
		_frame.geoRefPolygon = geo_polygon
		_frame.save()

		# TODO - FIND BEST WAY TO ANALYZE WKT IN JS!!
		param['georreferenced'] = wkt_str
	return render(request, "main/fire_progression.html", param)



# TODO: Animate Polygons
