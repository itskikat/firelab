# Generated by Django 3.1.2 on 2021-05-08 16:16

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20210507_2302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageframe',
            name='polygon',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, default=None, null=True, srid=4326),
        ),
    ]
