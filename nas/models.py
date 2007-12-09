from django.db import models

# Create your models here.

class Nas(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ipaddress = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    class Admin:
          ordering = ['-name']
          list_display = ('name','ipaddress','description')
    
    def __str__(self):
        return self.name
