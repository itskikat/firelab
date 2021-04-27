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


class Segmentation(forms.Form):
    pen = forms.BooleanField()
    eraser = forms.BooleanField()
    path = forms.CharField()
    image_id = forms.IntegerField()


