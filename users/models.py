from datetime import timedelta, timezone
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    country = models.CharField(max_length=20, null=False, blank=False)
    is_email_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.business_name 

