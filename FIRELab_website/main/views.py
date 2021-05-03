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
	# TODO: store polygon on db
	return redirect('/projects/' + str(project_id) + '/segmentation?id=' + str(file_id))


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
			return render(request, "main/fire_segmentation.html", param)

		img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, frame.content.name)))
		georreference = pickle.loads(frame.polygon)


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
		print(pixels_json)
		geo_json = json.loads(request.POST['geo'])
		print(geo_json)

		# if the frame_id is valid check if it has been georreferenced
		if _frame is None or _frame.polygon is None:
			return render(request, "main/fire_segmentation.html", param)

		img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _frame.content.name)))

		#TODO: Georeference points



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