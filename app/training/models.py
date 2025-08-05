from django.db import models
from core.models import User

class TrainingCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    style = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

class TrainingCourse(models.Model):
    title = models.CharField(max_length=255)
    short_description = models.TextField(max_length=300)
    category = models.ForeignKey(TrainingCategory, on_delete=models.SET_NULL, null=True, blank=True)
    course_url = models.URLField()
    thumbnail = models.ImageField(upload_to='training-thumbnails/', blank=True, null=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title 