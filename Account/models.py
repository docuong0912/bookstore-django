from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    # groups = models.ManyToManyField('auth.Group', related_name='account_user_groups', blank=True)
    # user_permissions = models.ManyToManyField('auth.Permission', related_name='account_user_permissions', blank=True)

    class Meta:
        db_table = 'user'