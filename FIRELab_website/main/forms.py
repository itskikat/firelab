from django import forms
from main.models import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm


class CreateAccountForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Email'}),
                             help_text='Please inform a valid email address')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Password'})
        }

    def _init_(self, *args, **kwargs):
        super(CreateAccountForm, self)._init_(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password confirmation'})


class UploadImage(forms.Form):
    image = forms.ImageField(label="Image")

    def __init__(self, *args, **kwargs):
        super(UploadImage, self).__init__(*args, **kwargs)
        self.fields['image'].widget.attrs = ({'class': 'file-upload__input', 'name': 'videoFile', 'id': 'videoFile'})


class UploadVideo(forms.Form):
    video = forms.FileField(label="Video")
    frames = forms.IntegerField(label="Number of frames")

    def __init__(self, *args, **kwargs):
        super(UploadVideo, self).__init__(*args, **kwargs)
        self.fields['video'].widget.attrs = ({'class': 'file-upload__input', 'name': 'videoFile', 'id': 'videoFile'})


class Segmentation(forms.Form):
    pen = forms.BooleanField()
    eraser = forms.BooleanField()
    path = forms.CharField()
    image_id = forms.IntegerField()


class ProjectCreation(forms.Form):
    name = forms.CharField(max_length=30, label="Project Name")
    description = forms.CharField(label="Description", max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        super(ProjectCreation, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = ({'id': 'project_name', 'placeholder': 'Enter project name', 'name': 'project_name'})
        self.fields['description'].widget.attrs = ({'id': 'project_description', 'placeholder': 'Add a description to your project (optional)', 'name': 'project_description'})


class Georreferencing(forms.Form):
    marker = forms.BooleanField()
    eraser = forms.BooleanField()
    pixels = forms.CharField()
    geo = forms.CharField()
    frame_id = forms.IntegerField()

class UploadCoordFile(forms.Form):
    coords = forms.FileField(label="File with Polygon Coordinates")
    image_id = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(UploadCoordFile, self).__init__(*args, **kwargs)
        self.fields['coords'].widget.attrs = ({'class': 'file-upload__input', 'name': 'coordsFile', 'id': 'coordsFile'})
        