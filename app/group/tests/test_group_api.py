"""
Tests for the Group API
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Group, GroupMembership
from group.serializers import (GroupMembershipSerializer,
                               GroupMembersListSerializer)

GROUPS_URL = reverse('group:groupmembership-list')
GROUP_MEMBERS_URL = reverse('group:groupmembership-members')


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


class PublicGroupAPITests(TestCase):
    """Tests the unauthenticated user requests in Group API"""

    def setUp(self):
        self.client = APIClient()

    def test_authentication(self):
        """Tests that only authenticated user can call the group API"""

        res = self.client.get(GROUPS_URL)
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

    def test_get_groups_for_user(self):
        """Tests retrieving groups for the user"""

        group1 = create_group(self.user, group_name="Test Group 1")
        create_group_membership(self.user, group1, 'Admin')

        group2 = create_group(self.user, group_name="Test Group 2")
        create_group_membership(self.user, group2, 'Admin')

        res = self.client.get(GROUPS_URL)
        group_membership = GroupMembership.objects.all()  # .order_by['-id']
        serializer = GroupMembershipSerializer(group_membership, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_groups_returned_for_authenticated_user_only(self):
        """Tests groups returned are limited to authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='testUser2@example.com',
            password='testPass111',
            date_of_birth='1990-05-09',
        )
        group1 = create_group(self.user, group_name="Test Group 1")
        create_group_membership(self.user, group1, 'Admin')

        group2 = create_group(user2, group_name="Test Group 2")
        create_group_membership(user2, group2, 'Admin')

        res = self.client.get(GROUPS_URL)
        group_membership = GroupMembership.objects.filter(member=self.user)
        serializer = GroupMembershipSerializer(group_membership, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_groups_returned_for_non_admin_user(self):
        """Tests groups returned are limited to authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='testUser2@example.com',
            password='testPass111',
            date_of_birth='1990-05-09',
        )
        group1 = create_group(user2, group_name="Test Group 1")
        create_group_membership(user2, group1, 'Admin')

        create_group_membership(self.user, group1, 'Member')

        res = self.client.get(GROUPS_URL)
        group_membership = GroupMembership.objects.filter(member=self.user)
        serializer = GroupMembershipSerializer(group_membership, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_group_names_only_request(self):
        """Tests that custom action returns group names only"""
        user2 = get_user_model().objects.create_user(
            email='testUser2@example.com',
            password='testPass111',
            date_of_birth='1990-05-09',
        )
        user3 = get_user_model().objects.create_user(
            email='testUser3@example.com',
            password='testPass221',
            date_of_birth='1993-02-11',
        )

        group1 = create_group(user2, group_name="Test Group 1")
        create_group_membership(user2, group1, 'Admin')

        create_group_membership(self.user, group1, 'Member')
        create_group_membership(user3, group1, 'Member')

        res = self.client.get(GROUP_MEMBERS_URL, {'group_id': group1.id})
        group_membership = GroupMembership.objects.filter(group=group1)
        serializer = GroupMembersListSerializer(group_membership, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
