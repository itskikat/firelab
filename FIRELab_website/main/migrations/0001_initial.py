# Generated by Django 3.1.12 on 2021-06-19 08:38

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import main.models
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subdirectories', to='main.directory')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FileInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('extension', models.CharField(max_length=10)),
                ('dir', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.directory')),
            ],
        ),
        migrations.CreateModel(
            name='FuelModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Grid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topLeftCoordinate', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=2)),
                ('bottomRightCoordinate', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=2)),
                ('gridded_image', models.ImageField(blank=True, default=None, null=True, upload_to='grids/')),
                ('cell_size', models.PositiveIntegerField()),
                ('file_info', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.fileinfo')),
                ('model', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.fuelmodel')),
            ],
        ),
        migrations.CreateModel(
            name='ImageFrame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.ImageField(upload_to=main.models.image_path)),
                ('mask', models.BinaryField(blank=True, default=None, null=True)),
                ('polygon', django.contrib.gis.db.models.fields.PolygonField(blank=True, default=None, null=True, srid=4326)),
                ('geoRefPolygon', django.contrib.gis.db.models.fields.PolygonField(blank=True, default=None, null=True, srid=4326)),
                ('timestamp', models.FloatField(blank=True, default=None, null=True)),
                ('file_info', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.fileinfo')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frame_number', models.IntegerField()),
                ('name', models.CharField(max_length=50)),
                ('extension', models.CharField(max_length=10)),
                ('content', models.FileField(blank=True, default=None, null=True, upload_to='videos/')),
            ],
        ),
        migrations.CreateModel(
            name='Tile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=2)),
                ('classification', models.IntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(4)])),
                ('avgColor', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(255)]), size=3)),
                ('grid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.grid')),
                ('start_time_frame', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.imageframe')),
            ],
        ),
        migrations.CreateModel(
            name='ReferencePoints',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geo_coordinates', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('name', models.CharField(max_length=30)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.project')),
            ],
        ),
        migrations.CreateModel(
            name='PointsInFrame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pixel_coordinate', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('frame', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.imageframe')),
                ('point', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.referencepoints')),
            ],
        ),
        migrations.CreateModel(
            name='PointModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('pix', django.contrib.gis.db.models.fields.PointField(blank=True, default=None, null=True, srid=4326)),
                ('geo', django.contrib.gis.db.models.fields.PointField(blank=True, default=None, null=True, srid=4326)),
                ('frame', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.imageframe')),
            ],
        ),
        migrations.CreateModel(
            name='Ortophoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.FileField(blank=True, default=None, null=True, upload_to='ortophotos/')),
                ('thumbnail', models.ImageField(blank=True, default=None, null=True, upload_to='ortophotos/thumbnails')),
                ('file_info', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.fileinfo')),
            ],
        ),
        migrations.AddField(
            model_name='imageframe',
            name='video',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.video'),
        ),
        migrations.AddField(
            model_name='grid',
            name='ortophoto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ortophoto'),
        ),
        migrations.AddField(
            model_name='directory',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.project'),
        ),
        migrations.CreateModel(
            name='Classification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('minPercentage', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('maxPercentage', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('hexColor', models.CharField(max_length=6)),
                ('classificationIndex', models.IntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('model', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.fuelmodel')),
            ],
        ),
    ]
