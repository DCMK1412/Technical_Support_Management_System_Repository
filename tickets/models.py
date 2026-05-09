from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('SUPPORT', 'Support'),
        ('USER','User'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='USER')

    def __str__(self):
        return f"{self.username} - {self.role}"
    
    