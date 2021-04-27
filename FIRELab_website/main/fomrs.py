from django import forms
from main.models import *


class UploadImage(forms.Form):
    image = forms.ImageField(label="Image")


class Segmentation(forms.Form):
    mode = forms.BooleanField()
    path = forms.CharField()
    image_id = forms.IntegerField()
