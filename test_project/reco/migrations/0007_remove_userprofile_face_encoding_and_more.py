# Generated by Django 5.1 on 2024-09-01 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reco', '0006_userprofile_delete_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='face_encoding',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='face',
            field=models.ImageField(default=True, upload_to='userDatabase/'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='password',
            field=models.CharField(default=True, max_length=30),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='username',
            field=models.CharField(default=True, max_length=15),
        ),
    ]
