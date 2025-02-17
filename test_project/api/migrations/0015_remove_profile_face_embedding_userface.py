# Generated by Django 5.1 on 2024-10-18 00:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_profile_face_embedding'),
        ('auth', '0014_remove_user_unique_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='face_embedding',
        ),
        migrations.CreateModel(
            name='UserFace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('embedding', models.BinaryField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
    ]
