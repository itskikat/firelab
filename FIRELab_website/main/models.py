from django.db import models
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey
# to delete media on object deletion
from django.db.models.signals import pre_delete, post_delete
from django.dispatch.dispatcher import receiver


# Create your models here.
# FILE STRUCTURE MODELS
class Project(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100, default=None, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "[Project {}] {}".format(self.id, self.name)


class Directory(MPTTModel):
    name = models.CharField(max_length=30)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='subdirectories')

    def __str__(self):
        return "{} - {} ({})".format(self.id, self.name, self.get_path())

    def get_path(self):
        current = self
        path_str = ''
        while current.parent is not None:
            path_str = '/' + current.name + path_str
            current = current.parent

        return '~' + path_str


class FileInfo(models.Model):
    name = models.CharField(max_length=50)
    extension = models.CharField(max_length=10)
    dir = models.ForeignKey(Directory, on_delete=models.CASCADE)

    def __str__(self):
        full_name = self.name
        if self.extension:
            full_name += "." + self.extension
        return str(self.id) + " - " + full_name

    def get_path(self):
        return self.dir.get_path() + "/" + self.name + "." + self.extension


class Video(models.Model):
    frame_number = models.IntegerField(blank=False)
    name = models.CharField(max_length=50)
    extension = models.CharField(max_length=10)
    content = models.FileField(upload_to='videos/', blank=True, null=True, default=None)

    def __str__(self):
        return "{} - Video ({}.{})".format(self.id, self.name, self.extension)


# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=Video)
def video_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.content is not None:
        instance.content.delete(False)


def image_path(instance, filename):
    if instance.video is not None:
        # video frame will be uploaded to MEDIA_ROOT/frames/<video_name>/
        return 'frames/{}/p{}_{}'.format(instance.video.name, instance.file_info.dir.project.id, filename)
    else:
        # image will be uploaded to  MEDIA_ROOT/images/
        return 'images/p{}_{}'.format(instance.file_info.dir.project.id, filename)


class ImageFrame(models.Model):
    content = models.ImageField(upload_to=image_path, blank=False)
    file_info = models.OneToOneField(FileInfo, on_delete=models.CASCADE, blank=False)
    mask = models.BinaryField(blank=True, null=True, default=None)
    polygon = models.CharField(max_length=100, blank=True, null=True, default=None)  # change to postGis polygon
    # add geo-referenced polygon field
    video = models.ForeignKey(Video, on_delete=models.CASCADE, blank=True, default=None, null=True)

    def __str__(self):
        return "{} - Frame ({})".format(self.id, self.get_filename())

    def get_filename(self):
        return "{}.{}".format(self.file_info.name, self.file_info.extension)


# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=ImageFrame)
def video_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.content is not None:
        instance.content.delete(False)