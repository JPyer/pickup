# Generated by Django 3.0.1 on 2020-10-04 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0009_auto_20201004_2013'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='devicelist',
            name='audio_bitrate',
        ),
        migrations.RemoveField(
            model_name='devicelist',
            name='audio_encoder',
        ),
        migrations.RemoveField(
            model_name='devicelist',
            name='audio_frame_size',
        ),
        migrations.RemoveField(
            model_name='devicelist',
            name='output_channel',
        ),
    ]
