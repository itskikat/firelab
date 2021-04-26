from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from main import views


urlpatterns = [
    path('', views.indexView, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path("signup/", views.createAccountView, name="signup"),
    path("projects", views.projects, name="projects"),
    path("account", views.account, name="account"),
    path("process", views.process, name="process"),
    path("vegetation", views.vegetation, name="vegetation"),
    path("segmentation", views.segmentation, name="segmentation"),
    path("progression", views.progression, name="progression"),
]