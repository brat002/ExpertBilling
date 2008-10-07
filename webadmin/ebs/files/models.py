from django.db import models

# Create your models here.

class FileCategory(models.Model):
    name = models.CharField(max_length=255)

class File(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='file/')
    category = models.ForeignKey(FileCategory)