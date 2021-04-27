import json
import pickle

import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse

from FIRELab_website.settings import MEDIA_ROOT
from main import utils
from main.fomrs import *
import cv2
import os
import numpy as np

# Create your views here.

def index(response):
	return render(response, "main/home.html", {})

def login(response):
	return render(response, "main/login.html", {})

def signup(response):
	return render(response, "main/signup.html", {})

def projects(response):
	return render(response, "main/projects.html", {})

def frontpage(response):
	return render(response, "main/front_page.html", {})

def account(response):
	return render(response, "main/account.html", {})

def process(response):
	return render(response, "main/project_process.html", {})

def vegetation(response):
	return render(response, "main/vegetation_characterization.html", {})


def upload(request):
	if request.method == 'POST':
		form = UploadImage(request.POST, request.FILES)
		if form.is_valid():
			name, extension = request.FILES['image'].name.split('.')

			try:
				# file already exists in the server
				FileInfo.objects.get(name=name, extension=extension)
				return HttpResponse("There is a file with that name already")

			except FileInfo.DoesNotExist:
				# create file info
				_file_info = FileInfo(
					name=name,
					extension=extension,
					type_id=FileType.objects.get(id=2),
					dir=Directory.objects.get(id=2)
				)
				_file_info.save()
				_image = Image(
					file_info= _file_info,
					content=request.FILES['image']
				)
				_image.save()

			img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _image.content.name)))

			# create empty mask of image's size
			_mask = np.zeros(img.shape[:2], np.uint8)
			# "serialize" the mask
			mask_encoded = pickle.dumps(_mask)

			# create mask file
			mask_file = FileInfo(
				name=_file_info.name,
				extension='mask',
				type_id=FileType.objects.get(type="Mask"),
				dir=Directory.objects.get(id=3)
			)
			mask_file.save()

			# create mask
			mask = Mask(
				file_info=mask_file,
				content=mask_encoded,
				image_id=_image
			)
			mask.save()

	return redirect("/segmentation")


def segmentation(response):
	if response.method == "GET":
		image = None
		if 'id' in response.GET:
			try:
				image = Image.objects.get(file_info__id=response.GET['id'])
			except Image.DoesNotExist:
				image = None

		param = {
			'file_list': FileInfo.objects.all(),
			'image': image,
			'form': UploadImage(),
			'segmentation': Segmentation(),
		}
		return render(response, "main/fire_segmentation.html", param)

	elif response.method == "POST":
		param = {
			'file_list': FileInfo.objects.all(),
			'image': None,
			'form': UploadImage(),
			'segmentation': Segmentation(initial={"mode": False}),
		}

		mode = False
		if 'mode' in response.POST:
			param['segmentation'] = Segmentation(initial={"mode": True})
			mode = True

		# check if image exists
		_id = response.POST['image_id']
		try:
			_image = Image.objects.get(file_info__id=_id)
			_image_file = _image.file_info
			param['image'] = _image

		except Image.DoesNotExist:
			return render(response, "main/fire_segmentation.html", param)

		if 'path' not in response.POST:
			return render(response, "main/fire_segmentation.html", param)

		# compute the path from the coordinates
		path_json = json.loads(response.POST['path'])
		path = np.array(path_json)
		mouse_path = path.astype(np.int)

		# if the image_id is valid check if it has a mask
		try:
			_mask = Mask.objects.get(image_id=_image)

		except Mask.DoesNotExist:
			return render(response, "main/fire_segmentation.html", param)

		img = cv2.imread(os.path.abspath(os.path.join(MEDIA_ROOT, _image.content.name)))
		mask = pickle.loads(_mask.content)

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
		_mask.content = mask_encoded
		_mask.save()

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


def progression(response):
	return render(response, "main/fire_progression.html", {})