# Generated by Django 5.1 on 2024-09-25 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_verificationcode'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrimeData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('community_area', models.FloatField()),
                ('date', models.DateField()),
                ('primary_type', models.IntegerField()),
                ('year', models.IntegerField()),
                ('crime_count', models.IntegerField()),
                ('total_crimes_per_type', models.IntegerField()),
                ('crime_rate', models.FloatField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
    ]
