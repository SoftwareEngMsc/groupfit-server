"""
Tests for models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


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
