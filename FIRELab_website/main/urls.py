from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from main import views


urlpatterns = [
    path('', views.indexView, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', views.createAccountView, name='signup'),
    path("projects", views.projects, name="projects"),
    path("home", views.frontpage, name="frontpage"),
    path("account", views.account, name="account"),
    path("projects/<int:project_id>/process", views.process, name="process"),
    path("projects/<int:project_id>/vegetation", views.vegetation, name="vegetation"),
    path("projects/<int:project_id>/vegetation/upload", views.upload_orthphoto, name="upload_ortophoto"),
    path("projects/<int:project_id>/vegetation/auto/<int:grid_id>", views.auto_classifier, name="auto_classifier"),
    path("projects/<int:project_id>/segmentation", views.segmentation, name="segmentation"),
    path("projects/<int:project_id>/segmentation/upload", views.upload, name="upload"),
    path("projects/<int:project_id>/segmentation/uploadVideo", views.upload_video, name="uploadVideo"),
    path("projects/<int:project_id>/segmentation/save/<int:file_id>", views.generate_contour, name="upload"),
    path("projects/<int:project_id>/progression", views.progression, name="progression"),
]
