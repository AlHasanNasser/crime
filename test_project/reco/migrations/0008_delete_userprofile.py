# Generated by Django 5.1 on 2024-09-01 06:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reco', '0007_remove_userprofile_face_encoding_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
