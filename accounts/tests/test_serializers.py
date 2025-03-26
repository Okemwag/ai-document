from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Profile
from accounts.serializers import (ProfileSerializer, TokenSerializer,
                                  UserLoginSerializer, UserRegisterSerializer)
from accounts.types import GenericToken


class TokenSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.token = RefreshToken.for_user(self.user)

    def test_valid_token(self):
        data = {"refresh": str(self.token)}
        serializer = TokenSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIn("access", serializer.validated_data)

    def test_invalid_token(self):
        data = {"refresh": "invalid_token"}
        serializer = TokenSerializer(data=data)
        try:
            serializer.is_valid()
        except Exception as e:
            self.assertIn("Token is invalid", str(e))


class UserLoginSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_valid_login(self):
        data = {
            "username": "testuser",
            "password": "testpass123",
        }
        serializer = UserLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.save(), self.user)

    def test_invalid_login(self):
        data = {
            "username": "testuser",
            "password": "wrongpassword",
        }
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)


class UserRegisterSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="existinguser", email="existing@example.com", password="testpass123"
        )

    def test_valid_registration(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
        }
        serializer = UserRegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, "newuser")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_duplicate_user(self):
        data = {
            "username": "existinguser",
            "email": "existing@example.com",
            "password": "newpassword123",
        }
        serializer = UserRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)


class ProfileSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.profile = Profile.objects.create(
            user=self.user, metadata={"profile_picture": "test.jpg"}
        )

    def test_profile_serializer(self):
        serializer = ProfileSerializer(instance=self.profile)
        self.assertEqual(serializer.data["user"]["username"], "testuser")
        self.assertEqual(serializer.data["metadata"]["profile_picture"], "test.jpg")

    @patch("accounts.serializers.ProfileSerializer.get_profile_picture")
    def test_profile_picture_missing(self, mock_get_profile_picture):
        mock_get_profile_picture.return_value = None
        serializer = ProfileSerializer(instance=self.profile)
        self.assertIsNone(serializer.data["profile_picture"])


