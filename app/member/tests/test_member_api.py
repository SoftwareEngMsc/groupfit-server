"""
Tests for the member API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_MEMBER_URL = reverse('member:create')
TOKEN_URL = reverse('member:token')
ME_URL = reverse('member:me')


def create_member(**params):
    """Create and return a new member"""

    return get_user_model().objects.create_user(**params)


class PublicMemberApiTests(TestCase):
    """ Test the public features of the member API"""

    def setUp(self):
        self.client = APIClient()

    def create_member_successful(self):
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

    def test_create_token_for_member(self):
        """Tests generates token as expected"""

        member_details = {
            'email': 'test@example.com',
            'password': 'pass',
            'firstname': 'Test First Name',
            'lastname': 'Test Last Name',
            'date_of_birth': '1988-09-21',
        }

        create_member(**member_details)

        payload = {
            'email': member_details['email'],
            'password': member_details['password']
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Tests an error is returned if credentials are invalid"""
        create_member(email='test@example.com', password='goodPassword')

        payload = {'email': 'test@example.com', 'password': 'badPassword'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_empty_password(self):
        """Tests an error is returned if password is empty"""

        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_retrieve_user_unauthorized(self):
    #     """Test authentication is required for users"""
    #     res = self.client.get(ME_URL)

    #     self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMemberApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.member = create_member(
            email='test@example.com',
            password='testpass123',
            firstname='Test First Name',
            lastname='Test Last Name',
            date_of_birth='1988-09-21',
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.member)

    def test_retrieve_member_profile_success(self):
        """Test able to retrieve the profile for the logged in member"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.member.email,
            'firstname': self.member.firstname,
            'lastname': self.member.lastname,
            'date_of_birth': self.member.date_of_birth,
        })

    def test_post_me_not_allowed(self):
        """Tests that POST is not allowed for the ME endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_member_profile(self):
        """Tests member profile can be updated when member authenticated"""
        payload = {'firstname': 'updated firstname',
                   'password': 'newPassWord123'}

        res = self.client.patch(ME_URL, payload)

        self.member.refresh_from_db()
        self.assertEqual(self.member.firstname, payload['firstname'])
        self.assertTrue(self.member.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
