from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(response):
	return render(response, "main/home.html", {})

def signup(response):
	return render(response, "main/signup.html", {})

def projects(request):
	if request.user.is_authenticated:
		return render(request, "main/projects.html", {})

def account(response):
	return render(response, "main/account.html", {})

def process(response):
	return render(response, "main/project_process.html", {})

def vegetation(response):
	return render(response, "main/vegetation_characterization.html", {})

def segmentation(response):
	return render(response, "main/fire_segmentation.html", {})

def progression(response):
	return render(response, "main/fire_progression.html", {})