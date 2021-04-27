from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from main import views


urlpatterns = [
<<<<<<< HEAD
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
=======
    path('', views.index, name="index"),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
>>>>>>> parent of 694a9a9... now creating accounts
    path("signup", views.signup, name="signup"),
    path("projects", views.projects, name="projects"),
    path("home", views.frontpage, name="frontpage"),
    path("account", views.account, name="account"),
    path("process", views.process, name="process"),
    path("vegetation", views.vegetation, name="vegetation"),
    path("segmentation", views.segmentation, name="segmentation"),
    path("segmentation/upload", views.upload, name="upload"),
    path("progression", views.progression, name="progression"),
]