from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from tenant.models import Client

class CustomUser(AbstractUser):
    tenant = models.ForeignKey("tenant.Client", on_delete=models.SET_NULL, null=True, blank=True)


class FailedLoginAttempt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    attemted_at = models.DateTimeField(auto_now_add=True)