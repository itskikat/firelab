from django.urls import path

from . import views

urlpatterns = [
path("", views.index, name="index"),
path("login", views.login, name="login"),
path("signup", views.signup, name="signup"),
path("projects", views.projects, name="projects"),
path("home", views.frontpage, name="frontpage"),
path("account", views.account, name="account"),
path("process", views.process, name="process"),
path("vegetation", views.vegetation, name="vegetation"),
path("segmentation", views.segmentation, name="segmentation"),
path("progression", views.progression, name="progression"),
]