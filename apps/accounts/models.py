
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    role_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.role_name


class User(AbstractUser):
    role = models.ForeignKey(
    Role,
    on_delete=models.PROTECT,
    related_name='users'
)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.URLField(blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    REQUIRED_FIELDS = ['email', 'full_name']

    def __str__(self):
        return self.username
