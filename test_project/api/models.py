from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import numpy as np


class VerificationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    


class News(models.Model):
    title = models.CharField(max_length=20 ,default="")
    image=models.ImageField(upload_to="News/", null=True ,blank=True)
    
    body = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50]
class UserFace(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the user model
    face_embedding = models.BinaryField()  # Store the face embedding as binary data (or the image)

    def save_embedding(self, embedding):
        self.face_embedding = embedding.tobytes()  # Save as bytes
        self.save()

    def get_embedding(self):
        return np.frombuffer(self.face_embedding)  # Convert bytes back to numpy array
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    saved_news = models.ManyToManyField(News, blank=True)
    history = models.ManyToManyField(News, blank=True , related_name='profile_histories')
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class CrimeData(models.Model):
    community_area = models.FloatField()
    date = models.DateField()
    primary_type = models.IntegerField()
    year = models.IntegerField()
    crime_count = models.IntegerField()
    total_crimes_per_type = models.IntegerField()
    crime_rate = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    def __str__(self):
        return f"Crime in area {self.community_area} on {self.date}"
    

