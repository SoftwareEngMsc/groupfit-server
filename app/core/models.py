"""
Database models for GroupFit server
"""
import uuid
import os

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.conf import settings


def workout_evidence_image_file_path(instance, filename):
    """generate path for wokout evidence image file"""
    extension = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{extension}'

    return os.path.join('uploads', 'workout_evidence', filename)


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
    """Fitness Group"""
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


class GroupWorkout(models.Model):
    """exercise workout for group"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField(max_length=255)
    created_date = models.DateField(auto_now_add=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class GroupWorkoutEvidence(models.Model):
    """Member evidence for workout completed"""
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    workout = models.ForeignKey(GroupWorkout, on_delete=models.CASCADE)
    evidence_image = models.ImageField(
        null=True, upload_to=workout_evidence_image_file_path)
    comment = models.CharField(max_length=255)
    submission_date = models.DateField(auto_now_add=True)
