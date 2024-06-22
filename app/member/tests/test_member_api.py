"""
Tests for the member API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_MEMBER_URL = reverse('member:create')


def create_member(**params):
    """Create and return a new member"""

    return get_user_model().objects.create_user(**params)


class PublicMemberApiTests(TestCase):
    """ Test the public features of the member API"""

    def setUp(self):
        self.client = APIClient()

    def create_user_member_successful(self):
        """Tests that a member can be created successfully"""

        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'firstname': 'Test First Name',
            'lastname': 'Test Last Name',
            'date_of_birth': '1988-09-21',
        }

        res = self.client.post(CREATE_MEMBER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_member_exists_error(self):
        """Tests that an error is returned if a member already exists"""

        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'firstname': 'Test First Name',
            'lastname': 'Test Last Name',
            'date_of_birth': '1988-09-21',
        }

        create_member(**payload)
        res = self.client.post(CREATE_MEMBER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_length_error(self):
        """Tests an error is returned if the password is too short"""

        payload = {
            'email': 'test@example.com',
            'password': 'pass',
            'firstname': 'Test First Name',
            'lastname': 'Test Last Name',
            'date_of_birth': '1988-09-21',
        }

        res = self.client.post(CREATE_MEMBER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
