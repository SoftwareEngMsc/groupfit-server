"""
Database models for GroupFit server
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.conf import settings


class UserManager(BaseUserManager):
    """Manager for members"""

    def create_user(self, email, password=None, **extra_field):
        """Create, save and return a new user"""
        if not email:
            raise ValueError("A valid email address muxt be entered")
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return new super user"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Member in the system"""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    join_date = models.DateField(auto_now_add=True)
    date_of_birth = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class Group(models.Model):
    # """Fitness Group"""
    group_name = models.CharField(max_length=100)
    target_workout_number_per_week = models.PositiveIntegerField(null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.group_name


class GroupMembership(models.Model):
    """Association of members to groups"""
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member_role = models.CharField(max_length=25)
