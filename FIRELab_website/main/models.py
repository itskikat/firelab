from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.gis.db import models as gisModels
# to delete media on object deletion
from django.db.models.signals import pre_delete, post_delete
from django.dispatch.dispatcher import receiver
from django.contrib.postgres.fields import ArrayField


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
    name = models.CharField(max_length=30, null=False)
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

# class CoordsFile(models.Model):
#     file_info = models.OneToOneField(FileInfo, on_delete=models.CASCADE, blank=False)
#     content = models.FileField(upload_to='poligonos/', blank=True, null=True, default=None)

#     def __str__(self):
#         return "{} - CoordsFile ({}.{})".format(self.name, self.extension, self.content)


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
    polygon = gisModels.PolygonField(blank=True, default=None, null=True)
    geoRefPolygon = gisModels.PolygonField(blank=True, default=None, null=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, blank=True, default=None, null=True)

    timestamp = models.FloatField(blank=True, default=None, null=True)

    def __str__(self):
        return "{} - Frame ({})".format(self.id, self.get_filename())

    def get_filename(self):
        return "{}.{}".format(self.file_info.name, self.file_info.extension)

class PointModel(models.Model):
    name = models.CharField(max_length=50,unique=True)
    pix = gisModels.PointField(blank=True, default=None, null=True)
    geo = gisModels.PointField(blank=True, default=None, null=True)
    frame = models.ForeignKey(ImageFrame, on_delete=models.CASCADE, blank=True, default=None, null=True)
   
    def __str__(self):
        return "[Point {}]".format(self.name)



# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=ImageFrame)
def video_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.content is not None:
        instance.content.delete(False)


class Ortophoto(models.Model):
    content = models.FileField(upload_to='ortophotos/', blank=True, null=True, default=None)
    thumbnail = models.ImageField(upload_to="ortophotos/thumbnails", blank=True, null=True, default=None)
    file_info = models.OneToOneField(FileInfo, on_delete=models.CASCADE, blank=False)


# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=Ortophoto)
def ortophoto_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.content is not None:
        instance.content.delete(False)
    if instance.thumbnail is not None:
        instance.thumbnail.delete(False)


class FuelModel(models.Model):
    name = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return self.name


class Classification(models.Model):
    name = models.CharField(max_length=30)
    model = models.ForeignKey(FuelModel, on_delete=models.CASCADE, blank=True, null=True, default=None)
    minPercentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    maxPercentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    hexColor = models.CharField(max_length=6)
    classificationIndex = models.IntegerField(blank=True, null=True, default=None, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name + " (" + str(self.minPercentage) + "%-" + str(self.maxPercentage) + "%)"


class Grid(models.Model):
    topLeftCoordinate = ArrayField(models.IntegerField(blank=False), size=2)
    bottomRightCoordinate = ArrayField(models.IntegerField(blank=False), size=2)
    ortophoto = models.ForeignKey(Ortophoto, on_delete=models.CASCADE, blank=False)
    gridded_image = models.ImageField(upload_to="grids/", blank=True, null=True, default=None)
    cell_size = models.PositiveIntegerField(blank=False)
    model = models.ForeignKey(FuelModel, on_delete=models.CASCADE, blank=True, null=True, default=None)
    file_info = models.OneToOneField(FileInfo, on_delete=models.CASCADE, blank=False)


# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=Grid)
def grid_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.gridded_image is not None:
        instance.gridded_image.delete(False)



class Tile(models.Model):
    position = ArrayField(models.IntegerField(blank=False), size=2)
    classification = models.IntegerField(blank=True, default=None, null=True, validators=[MinValueValidator(0), MaxValueValidator(4)])
    avgColor = ArrayField(
        models.IntegerField(blank=True, null=True, default=None,
                            validators=[MinValueValidator(0), MaxValueValidator(255)]),
        size=3)
    grid = models.ForeignKey(Grid, on_delete=models.CASCADE)
    start_time_frame = models.ForeignKey(ImageFrame, on_delete=models.SET_NULL, blank=True, null=True, default=None)

    def __str__(self):
        return "tile(" + str(self.position) + "), avgColor: " + str(self.avgColor) + ", classification: " + str(self.classification)

