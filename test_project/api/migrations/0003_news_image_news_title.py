# Generated by Django 5.1 on 2024-09-05 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_news'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='News/'),
        ),
        migrations.AddField(
            model_name='news',
            name='title',
            field=models.CharField(default='', max_length=20),
        ),
    ]
