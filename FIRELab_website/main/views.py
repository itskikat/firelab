from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import update_session_auth_hash

from main.models import *
from main.forms import *
# Create your views here.

def indexView(request):
	return render(request, "main/home.html", {})

def signup(response):
	return render(response, "main/signup.html", {})

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