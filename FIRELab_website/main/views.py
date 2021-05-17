import io
import json
import math
import pickle

from django.core.files.images import ImageFile
from django.shortcuts import render, redirect
from FIRELab_website.settings import MEDIA_ROOT
from main import utils
from main.forms import *
import cv2
import os
import numpy as np
from django.http import HttpResponse

# Create your views here.
def indexView(response):
	return render(response, "main/home.html", {})

# Create new user account
def createAccountView(request):
	data = {}
	if request.method == 'POST':
		form = CreateAccountForm(request.POST)
		if form.is_valid():
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

				for d in ['Images', 'Masks', 'Frames']:
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

	param = {
		'project': project,
		'project_dirs': Directory.objects.all().filter(project_id=project.id),
		'project_files': FileInfo.objects.all().filter(dir__project_id=project.id),
	}
	return render(response, "main/vegetation_characterization.html", param)


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

def upload_polygon(request, project_id):
	if not request.user.is_authenticated:
		return redirect("/login")
	try:
		project = Project.objects.get(id=project_id)
	except Project.DoesNotExist:
		return redirect("/projects")
	if request.method == 'POST':
		polygon=request.FILES['coords'].read()
	print("images from upload poly")
	print(request.FILES['image'].name)


	return redirect("/projects/" + str(project_id) + "/progression")


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

			step = math.floor(max_frames/int(frame_number))
			cur_frame = 0
			frame_index = 1			# retrieved frame index

			frames_dir = Directory(
				name=name,
				project=project,
				parent=Directory.objects.get(project__id=project.id, name="Frames")
			)
			frames_dir.save()

			try:
				while video_capture.isOpened() and cur_frame < max_frames:
					_, frame = video_capture.read()		# read next image from video
					if cur_frame % step == 0:
						frame_name = "{}_{}".format(name, frame_index)

						_, frame_arr = cv2.imencode('.png', frame)  # Numpy one-dim array representative of the img
						frame_bytes = frame_arr.tobytes()
						_frame = ImageFile(io.BytesIO(frame_bytes), name='{}.png'.format(frame_name))

						# cv2.imshow('{}.png'.format(frame_name), frame)
						# cv2.waitKey(0)  # waits until a key is pressed
						# cv2.destroyAllWindows()  # destroys the window showing image

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

		# if the image_id is valid check if it has a mask
		if image is None or image.mask is None:
			return render(response, "main/fire_segmentation.html", param)

		img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, image.content.name)))
		mask = pickle.loads(image.mask	)

		mask_is_new = (mask == 0).all()
		if mask_is_new:
			return render(response, "main/fire_segmentation.html", param)

		# "serialize" the updated mask
		mask_encoded = pickle.dumps(mask)
		# update the mask file on db
		image.mask = mask_encoded
		image.save()

		mask_32S = mask.astype(np.int32)  # used to convert the mask to CV_32SC1 so it can be accepted by cv2.watershed()
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

		mask_32S = mask.astype(np.int32)  # used to convert the mask to CV_32SC1 so it can be accepted by cv2.watershed()
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
	vertexes,_ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
	
	if len(vertexes) > 1:
		print("More than one polygon were identified")
		# TODO: add return_bigger to Segmentation form and input on pop up
		# if 'return_bigger' in request.GET and request.GET['return_bigger'] == "1":
		sizes = [len(pol) for pol in vertexes]
		vertexes = vertexes[sizes.index(max(sizes))]
		#else:
			#return redirect("/segmentation?id=" + str(file_id)) + "&error=TooManyValues
	else:
		vertexes = vertexes[0]
	fs_wkt = ""
	for point in vertexes:
		fs_wkt += ", " + str(point[0][0]) + " " + str(point[0][1])
	fs_wkt = "POLYGON ((" + fs_wkt[2:] + ", " + str(vertexes[0][0][0]) + " " + str(vertexes[0][0][1]) + "))\n"
	_image.polygon =fs_wkt
	_image.save()
	# TODO: store polygon on db
	return redirect('/projects/' + str(project_id) + '/progression?id=' + str(file_id))


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
		#static polygon for tests
		#frame.polygon= "POLYGON ((261 277, 260 278, 260 279, 260 280, 260 281, 260 282, 260 283, 260 284, 261 285, 261 286, 262 286, 263 286, 264 286, 265 287, 265 288, 265 289, 265 290, 265 291, 264 292, 263 292, 262 292, 263 293, 264 293, 265 294, 265 295, 265 296, 265 297, 265 298, 264 299, 265 300, 265 301, 265 302, 266 303, 267 304, 268 305, 268 306, 269 307, 269 308, 269 309, 269 310, 269 311, 269 312, 268 313, 268 314, 268 315, 268 316, 268 317, 269 318, 269 319, 270 319, 271 319, 272 319, 273 319, 274 320, 275 321, 276 321, 277 321, 278 322, 278 323, 278 324, 278 325, 279 325, 280 326, 280 325, 280 324, 280 323, 280 322, 281 321, 282 321, 283 321, 284 320, 285 320, 286 319, 286 318, 287 317, 288 316, 288 315, 288 314, 288 313, 288 312, 288 311, 288 310, 288 309, 289 308, 290 307, 290 306, 289 305, 289 304, 288 303, 288 302, 288 301, 288 300, 288 299, 289 298, 288 297, 288 296, 288 295, 288 294, 287 294, 286 293, 285 293, 284 293, 283 293, 282 292, 281 292, 280 291, 279 290, 279 289, 279 288, 279 287, 279 286, 278 286, 277 285, 277 284, 277 283, 276 283, 275 283, 274 283, 273 283, 272 283, 271 283, 270 284, 269 284, 268 284, 267 284, 266 284, 265 284, 264 284, 263 283, 262 282, 262 281, 262 280, 262 279, 262 278, 262 277, 261 277))"
		# if the frame_id is valid check if it has been georreferenced
		if frame is None or frame.polygon is None:
			return render(request, "main/fire_progression.html", param)
		
		img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, frame.content.name)))
		
		return render(request, "main/fire_progression.html", param)

	elif request.method == 'POST':
		param = {
			'frame': None,
			'project': project,
			'project_dirs': Directory.objects.all().filter(project_id=project.id),
			'project_files': FileInfo.objects.all().filter(dir__project_id=project.id),
			'file_form': UploadCoordFile(),
			'georreferencing': Georreferencing(initial={"marker": False, "eraser": False}),
		}

		if 'frame_id' not in request.POST or request.POST['frame_id'] == '':
			return redirect(request.build_absolute_uri())
		mode = None
		if 'marker' in request.POST:
			param['georreferencing'] = Georreferencing(initial={'marker': True})
			mode = True

		if 'eraser' in request.POST:
			param['georreferencing'] = Georreferencing(initial={"eraser": True})
			mode = False

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
			print("frame")
			print(_frame)
			return render(request, "main/fire_segmentation.html", param)

		img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _frame.content.name)))

		#TODO: Georeference points
		pts_src = np.array(pixels_json)
		pts_dst = np.array(geo_json)
		#given reference points from 2 spaces, returns a matrix that can convert between the 2 spaces (in this case, pixel to geo coords)
		h, status = cv2.findHomography(pts_src, pts_dst) 
			

		#TODO read from file
		coords = _frame.polygon.split("((")[1].split("))")[0].split(",")
				
		geo_coords = ""
		wkt_str = ""
		for coord in coords:
			coord_split = coord.strip().split(" ")
			point_homogenous = h.dot([float(coord_split[0]), float(coord_split[1]), 1])
			if len(point_homogenous) != 3:
				geo_coord= [0,0]
			else:
				z = point_homogenous[2]
				geo_coord= [point_homogenous[0]/z, point_homogenous[1]/z]
			geo_coords = geo_coords + str(geo_coord[0]) + " " + str(geo_coord[1])+ ", "
		wkt_str = "POLYGON ((" + geo_coords 
		print(wkt_str[:-2]+"))")
		_frame.geoRefPolygon =wkt_str
		_frame.save()
		#TODO save georef polygon
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
	polygonm = pickle.loads(_frame.polygon)
	georeference = pickle.loads(_frame.georeference)

	



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

	_, vertexes, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

	if len(vertexes) > 1:
		print("More than one polygon were identified")
		# TODO: add return_bigger to Segmentation form and input on pop up
		# if 'return_bigger' in request.GET and request.GET['return_bigger'] == "1":
		sizes = [len(pol) for pol in vertexes]
		vertexes = vertexes[sizes.index(max(sizes))]
		#else:
			#return redirect("/segmentation?id=" + str(file_id)) + "&error=TooManyValues
	else:
		vertexes = vertexes[0]

	fs_wkt = ""
	for point in vertexes:
		fs_wkt += ", " + str(point[0][0]) + " " + str(point[0][1])
	fs_wkt = "POLYGON ((" + fs_wkt[2:] + ", " + str(vertexes[0][0][0]) + " " + str(vertexes[0][0][1]) + "))\n"
	print(fs_wkt)
	
	
	
	return redirect('/projects/' + str(project_id) + '/progression?id=' + str(file_id))
'''