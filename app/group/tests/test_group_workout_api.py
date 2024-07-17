"""
Tests for the Group API
"""

import tempfile
import os
from PIL import Image
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
GROUP_ADD_WORKOUT_URL = reverse(
    'group:workout-addWorkout', kwargs={'pk': None})
GROUP_DELETE_WORKOUT_URL = reverse(
    'group:workout-deleteWorkout', kwargs={'pk': None})
GROUP_WORKOUT_EVIDENCE_FOR_MEMBER_URL = reverse(
    'group:workout-evidence', kwargs={'pk': None})
GROUP_WORKOUT_EVIDENCE_LOG_FOR_MEMBER_URL = reverse(
    'group:workout-evidenceLog', kwargs={'pk': None})
GROUP_WORKOUT_UPLOAD_EVIDENCE_URL = reverse(
    'group:workout-uploadEvidence', kwargs={'pk': None})


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


class PublicGroupWorkoutAPITests(TestCase):
    """Tests the unauthenticated user requests in Group API"""

    def setUp(self):
        self.client = APIClient()

    def test_authentication(self):
        """Tests that only authenticated user can call the group API"""

        res = self.client.get(GROUP_WORKOUT_URL, {'group': 1})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGroupWorkoutAPITests(TestCase):
    """Tests the authenticated user requests in Group API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testUser@example.com',
            # first_name='firstName',
            # last_name='lastName',
            password='testPass123',
            # date_of_birth='1988-09-21',
        )
        self.client.force_authenticate(self.user)

    def test_add_workout_for_group(self):
        """Tests adding a workout for a group"""
        params = {
            'name': 'Test Workout',
            'description': 'Full body workout',
            'link': 'http://test.co.uk',
        }
        # workout = create_workout(self.user, **params)

        group = create_group(self.user)
        create_group_membership(self.user, group, 'Admin')

        payload = {
            'name': params['name'],
            'description': params['description'],
            'link': params['link'],
            'group_id': group.id,
        }
        res = self.client.post(GROUP_ADD_WORKOUT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['name'], params['name'])
        self.assertEqual(res.data['description'], params['description'])
        self.assertEqual(res.data['link'], params['link'])

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

    def test_delete_workout_for_group(self):
        """Tests that a group workout can be deleted successfully"""
        params = {
            'name': 'Test Workout',
            'description': 'Full body workout',
            'link': 'http://test.co.uk',
        }
        workout_to_delete = create_workout(self.user, **params)

        res = self.client.delete(
            GROUP_DELETE_WORKOUT_URL, {'workout_id': workout_to_delete.id})

        workout = GroupWorkout.objects.filter(
            id=workout_to_delete.id)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(workout.count(), 0)

    def test_get_workout_evidence_for_group_member_by_workout(self):
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
        res = self.client.get(GROUP_WORKOUT_EVIDENCE_FOR_MEMBER_URL, {
                              'member_id': self.user.id,
                              'workout_id': workout.id})
        workout_evidence = GroupWorkoutEvidence.objects.filter(
            workout=workout, member=self.user)

        serializer = GroupWorkoutEvidenceSerializer(
            workout_evidence, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_all_workout_evidence_for_group_member(self):
        """Tests retrieving workouts evidence for a group member"""

        evidence_params1 = {
            'comment': 'Fab workout!',
        }
        evidence_params2 = {
            'comment': 'Fab workout!',
        }

        group = create_group(self.user)
        create_group_membership(self.user, group, 'Admin')

        workout1 = GroupWorkout.objects.create(
            group=group,
            name='Test Workout',
            description='Full body workout',
            link='http://test.co.uk',
        )

        workout2 = GroupWorkout.objects.create(
            group=group,
            name='Test Workout2',
            description='Arm workout',
            link='http://test.co.uk',
        )

        create_workout_evidence(
            self.user, workout1, ** evidence_params1)
        create_workout_evidence(
            self.user, workout2, **evidence_params2)

        # TODO:  Create URL helper functions - check entire codebase
        print(GROUP_WORKOUT_EVIDENCE_LOG_FOR_MEMBER_URL)
        res = self.client.get(GROUP_WORKOUT_EVIDENCE_LOG_FOR_MEMBER_URL, {
                              'member_id': self.user.id,
                              'group_id': group.id})
        workout_evidence = GroupWorkoutEvidence.objects.filter(
            member=self.user, workout_id__in=[workout1.id, workout2.id])

        serializer = GroupWorkoutEvidenceSerializer(
            workout_evidence, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class UploadEvidenceTests(TestCase):
    """Workout evidence upload tests"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testUser@example.com',
            # first_name='firstName',
            # last_name='lastName',
            password='testPass123',
            # date_of_birth='1988-09-21',
        )
        self.client.force_authenticate(self.user)
        workout_params = {
            'name': 'Test Workout',
            'description': 'Full body workout',
            'link': 'http://test.co.uk',
        }
        evidence_params = {
            'comment': 'Fab workout!',
        }
        workout = create_workout(self.user, **workout_params)
        self.workout_evidence = create_workout_evidence(
            self.user, workout, **evidence_params)

    def tearDown(self):
        self.workout_evidence.evidence_image.delete()

    def test_evidence_upload(self):
        """Tests evidence is uploaded successfully"""

        with tempfile.NamedTemporaryFile(suffix='.jpg') as evidence_file:
            evidence = Image.new('RGB', (10, 20))
            evidence.save(evidence_file, format='JPEG')
            evidence_file.seek(0)
            payload = {
                'evidence_image': evidence_file,
                'workout_id': self.workout_evidence.workout.id,
            }

            res = self.client.post(
                GROUP_WORKOUT_UPLOAD_EVIDENCE_URL,
                payload,  format='multipart')

        self.workout_evidence.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('evidence_image', res.data)
        self.assertTrue(os.path.exists(
            self.workout_evidence.evidence_image.path))

    def test_evidence_upload_invalid_request(self):
        """Tests invalid evidence upload is handled"""

        payload = {'evidence_image': 'invalid request',
                   'workout_id': self.workout_evidence.workout.id,
                   }
        res = self.client.post(
            GROUP_WORKOUT_UPLOAD_EVIDENCE_URL, payload,  format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
