# Generated by Django 3.2 on 2021-06-02 22:34

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20210602_2225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pointmodel',
            name='geo',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, default=None, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='pointmodel',
            name='pix',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, default=None, null=True, srid=4326),
        ),
    ]
