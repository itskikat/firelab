# Generated by Django 3.1.2 on 2021-05-07 23:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20210507_2300'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tile',
            old_name='gird',
            new_name='grid',
        ),
    ]
