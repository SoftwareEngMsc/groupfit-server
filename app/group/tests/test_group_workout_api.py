"""
Tests for the Group API
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Group, GroupMembership,
                         GroupWorkout, GroupWorkoutEvidence)
from group.serializers import (GroupWorkoutSerializer,
                               GroupWorkoutEvidenceSerializer)

GROUP_WORKOUT_URL = reverse('group:workout-workout', kwargs={'pk': None})
GROUP_WORKOUT_EVIDENCE_URL = reverse(
    'group:workout-evidence', kwargs={'pk': None})


def create_group(user, **params):
    """creates a group for testing"""
    defaults = {
        'group_name': 'Test Group',
        'target_workout_number_per_week': 3,
    }

    defaults.update(params)

    group = Group.objects.create(
        created_by=user,
        **defaults
    )
    return group


def create_group_membership(user, group, role):
    """creates a Group Member entry for testing"""
    group_member = GroupMembership.objects.create(
        member=user,
        group=group,
        member_role=role
    )
    return group_member


def create_workout(user, **params):
    """Create workout entry for group"""
    defaults = {
        'name': 'Test Workout',
        'description': 'Full body workout',
        'link': 'http://test.co.uk',
    }

    defaults.update(params)

    group = create_group(user)
    create_group_membership(user, group, 'Admin')

    workout = GroupWorkout.objects.create(
        group=group,
        **defaults
    )
    return workout


def create_workout_evidence(user, workout, **params):
    """Create workout evidence entry for workout/user"""
    defaults = {
        'comment': 'Superb!',
    }

    defaults.update(params)

    workout_evidence = GroupWorkoutEvidence.objects.create(
        member=user,
        workout=workout,
        # evidence_item=
        **defaults
    )
    return workout_evidence


def evidence_upload_url(member_id, group_id):
    """Creates and returns anevidence upload url"""
    kwargs = {
        'member_id': member_id,
        'group_id': group_id
    }
    return reverse('group:workout-upload-evidence', kwargs=kwargs)


class PublicGroupAPITests(TestCase):
    """Tests the unauthenticated user requests in Group API"""

    def setUp(self):
        self.client = APIClient()

    def test_authentication(self):
        """Tests that only authenticated user can call the group API"""

        res = self.client.get(GROUP_WORKOUT_URL, {'group': 1})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGroupAPITests(TestCase):
    """Tests the authenticated user requests in Group API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testUser@example.com',
            # first_name='firstName',
            # last_name='lastName',
            password='testPass123',
            date_of_birth='1988-09-21',
        )
        self.client.force_authenticate(self.user)

    def test_get_workout_for_group(self):
        """Tests retrieving workouts for a group"""
        params = {
            'name': 'Test Workout',
            'description': 'Full body workout',
            'link': 'http://test.co.uk',
        }
        workout = create_workout(self.user, **params)
        res = self.client.get(GROUP_WORKOUT_URL, {
                              'group_id': workout.group.id})
        workouts = GroupWorkout.objects.filter(
            group=workout.group)

        serializer = GroupWorkoutSerializer(workouts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_workout_evidence_for_group_member(self):
        """Tests retrieving workouts evidence for a group member"""
        workout_params = {
            'name': 'Test Workout',
            'description': 'Full body workout',
            'link': 'http://test.co.uk',
        }
        evidence_params = {
            'comment': 'Fab workout!',
        }
        workout = create_workout(self.user, **workout_params)
        create_workout_evidence(
            self.user, workout, **evidence_params)

        # TODO:  Create URL helper functions - check entire codebase
        res = self.client.get(GROUP_WORKOUT_EVIDENCE_URL, {
                              'member_id': self.user.id,
                              'workout_id': workout.id})
        workout_evidence = GroupWorkoutEvidence.objects.filter(
            workout=workout, member=self.user)

        serializer = GroupWorkoutEvidenceSerializer(
            workout_evidence, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
