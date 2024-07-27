"""Tests for the Firnds API"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Friends
from friends.serializers import FriendsSerializer

FRIENDS_URL = reverse('friends:friends-getFriends')
FRIENDS_ADD_URL = reverse('friends:friends-addFriend', kwargs={'pk': None})
FRIENDS_ACCEPT_REJECT_RESPONSE_URL = reverse(
    'friends:friends-response', kwargs={'pk': None})


def create_friend_connection(requestingUser, otherUser):
    params = {
        'user1': requestingUser,
        'user2': otherUser,
        'status': 'Pending',
        'requested_by': requestingUser,
    }

    friend_connection = Friends.objects.create(**params)
    return friend_connection


def create_user(**params):
    defaults = {
        'email': 'testUser@example.com',
        'first_name': 'firstName',
        'last_name': 'lastName',
        'password': 'testPass123',
        # 'date_of_birth': '1988-09-21',
    }

    defaults.update(params)

    user = get_user_model().objects.create_user(**defaults)
    return user


class PublicFriendsAPITests(TestCase):
    """Tests the unauthenticated user requests in Friends API"""

    def setUp(self):
        self.client = APIClient()

    def test_authentication(self):
        """Tests that only authenticated user can call the Friends API"""

        res = self.client.get(FRIENDS_URL, {'user_id': 1})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateFriendsAPITests(TestCase):
    """Tests the authenticated user requests in Group API"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_get_friends_for_user(self):
        """Test getting the friend connections for a user"""
        params = {
            'email': 'user2@example.com',
            'first_name': 'firstName2',
            'last_name': 'lastName2',
            'password': 'testPass1234',
            # 'date_of_birth': '1998-09-21',
        }
        user2 = create_user(**params)

        create_friend_connection(self.user, user2)
        friend_connection = Friends.objects.filter(user1=self.user)
        serializer = FriendsSerializer(friend_connection, many=True)

        res = self.client.get(FRIENDS_URL, {'user_id': self.user.id})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_add_friend_connection(self):
        """Test add a new friend connections"""
        params = {
            'email': 'user2@example.com',
            'first_name': 'firstName2',
            'last_name': 'lastName2',
            'password': 'testPass1234',
            # 'date_of_birth': '1998-09-21',
        }
        user2 = create_user(**params)

        payload = {
            'requested_by_id': self.user.id,
            'user2_id': user2.id
        }

        res = self.client.post(FRIENDS_ADD_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['user1'].get('email'), self.user.email)
        self.assertEqual(res.data['user2'].get('email'), user2.email)
        self.assertEqual(res.data['requested_by'].get(
            'email'), self.user.email)
        self.assertEqual(res.data['status'], 'Pending')

    def test_accept_friend_request(self):
        """Tests friend request can be accepted"""
        params = {
            'email': 'user2@example.com',
            'first_name': 'firstName2',
            'last_name': 'lastName2',
            'password': 'testPass1234',
            # 'date_of_birth': '1998-09-21',
        }
        user2 = create_user(**params)

        friend_connection = create_friend_connection(self.user, user2)

        updated_status = 'Accepted'
        response = {
            'friend_conn_id': friend_connection.id,
            'status': updated_status,
        }
        res = self.client.patch(FRIENDS_ACCEPT_REJECT_RESPONSE_URL, response)

        friend_connection.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(friend_connection.status, updated_status)

    def test_reject_friend_request(self):
        """Tests friend request can be accepted"""
        params = {
            'email': 'user2@example.com',
            'first_name': 'firstName2',
            'last_name': 'lastName2',
            'password': 'testPass1234',
            # 'date_of_birth': '1998-09-21',
        }
        user2 = create_user(**params)

        friend_connection = create_friend_connection(self.user, user2)

        updated_status = 'Rejected'
        response = {
            'friend_conn_id': friend_connection.id,
            'status': updated_status,
        }
        res = self.client.patch(FRIENDS_ACCEPT_REJECT_RESPONSE_URL, response)

        print(res)
        friend_connection_updated = Friends.objects.filter(
            id=friend_connection.id)

        self.assertEqual(friend_connection_updated.count(), 0)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # self.assertEqual(res.message, 'Friend Connection Rejected')

    def test_delete_friend(self):
        """Tests a friend can be deleted"""
        params = {
            'email': 'user2@example.com',
            'first_name': 'firstName2',
            'last_name': 'lastName2',
            'password': 'testPass1234',
            # 'date_of_birth': '1998-09-21',
        }
        user2 = create_user(**params)

        friend_connection_to_delete = create_friend_connection(
            self.user, user2)

        updated_status = 'Rejected'
        response = {
            'friend_conn_id': friend_connection_to_delete.id,
            'status': updated_status,
        }

        FRIENDS_DELETE_URL = reverse(
            'friends:friends-deleteFriend',
            kwargs={'pk': friend_connection_to_delete.id})
        res = self.client.delete(FRIENDS_DELETE_URL, response)

        friend_connection = Friends.objects.filter(
            id=friend_connection_to_delete.id)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(friend_connection.count(), 0)
