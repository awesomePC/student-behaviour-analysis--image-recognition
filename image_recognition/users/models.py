from django.contrib.auth.models import AbstractUser
from django.db import models

from .choices import USER_TYPE_CHOICES

class CustomUser(AbstractUser):
    # super user only created from command prompt
    user_type = models.CharField(
        max_length=15,
        choices=USER_TYPE_CHOICES
    )
    phone = models.CharField(max_length=10, null=True, blank=True)
    
    # REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email

