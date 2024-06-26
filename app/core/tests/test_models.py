"""
Tests for models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successul(self):
        """Test creating a user with an email is successful"""
        email = "testUser@example.com"
        password = "testPass123"
        member = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(member.email, email)
        self.assertTrue(member.check_password(password))

    def test_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
        ]

        for email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self):
        """Test that a ValueError is raised for a new user without an email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testUser')

    def test_create_superuser(self):
        """Test creation of super user"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)

    def test_create_group(self):
        """Test to ensure group is created as expected"""

        user = get_user_model().objects.create_user(
            email='testUser@example.com',
            # first_name='firstName',
            # last_name='lastName',
            # password='testPass123',
            date_of_birth='1988-09-21',
        )

        group = models.Group.objects.create(
            group_name='Test Group',
            target_workout_number_per_week=3,
            created_by=user
        )

        self.assertEqual(str(group), group.group_name)
        self.assertEqual(user.email, group.created_by.email)

    def test_create_group_member(self):
        """Tests that the goup member model is created"""

        user = get_user_model().objects.create_user(
            email='testUser@example.com',
            date_of_birth='1988-09-21',
        )

        group = models.Group.objects.create(
            group_name='Test Group',
            target_workout_number_per_week=3,
            created_by=user
        )

        group_member = models.GroupMembership.objects.create(
            member=user,
            group=group,
            member_role='Admin'
        )

        self.assertEqual(user.email, group_member.member.email)
        self.assertEqual(str(group), group_member.group.group_name)
        self.assertEqual(group_member.member_role, 'Admin')
