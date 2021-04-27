from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# FILE STRUCTURE MODELS
class Project(models.Model):
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "[Project {}] {}".format(self.id, self.name)


class Directory(models.Model):
    name = models.CharField(max_length=30)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='directory')

    def __str__(self):
        return "{} - {} ({})".format(self.id, self.name, self.get_path())

    def get_path(self):
        current = self
        path_str = ''
        while current.parent is not None:
            path_str = '/' + current.name + path_str
            current = current.parent

        return '~' + path_str


class FileType(models.Model):
    type = models.CharField(max_length=30)

    def __str__(self):
        return str(self.id) + " - " + self.type


class FileInfo(models.Model):
    name = models.CharField(max_length=50)
    extension = models.CharField(max_length=10)
    dir = models.ForeignKey(Directory, on_delete=models.CASCADE)
    type_id = models.ForeignKey(FileType, on_delete=models.CASCADE)

    def __str__(self):
        full_name = self.name
        if self.extension:
            full_name += "." + self.extension
        return str(self.id) + " - " + full_name


class Image(models.Model):
    content = models.ImageField(upload_to='images/', blank=False)
    file_info = models.OneToOneField(FileInfo, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return "{} - Image ({})".format(self.id, self.get_filename())

    def get_filename(self):
        return "{}.{}".format(self.file_info.name, self.file_info.extension)


class Mask(models.Model):
    content = models.BinaryField(blank=False)
    file_info = models.OneToOneField(FileInfo, on_delete=models.CASCADE, blank=False)
    image_id = models.ForeignKey(Image, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return "{} - Mask ({})".format(self.id, self.get_filename())

    def get_filename(self):
        return "{}.{}".format(self.file_info.name, self.file_info.extension)
