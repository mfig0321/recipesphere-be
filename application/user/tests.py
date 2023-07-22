"""
Tests for user api
"""


from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status


def create_user(**params):
    """Create and return a new user."""

    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Test create user api"""
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating user successful"""

        payload = {
            'username': 'testuser1',
            'password': 'testpass001',
            'email': 'test001@example.com',
            'first_name': 'test_f_name001',
            'last_name': 'test_l_name001',
        }

        response = self.client.post('/api/createuser/', payload)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_with_email_exists_error(self):
        """"Test error returned if with email exists."""
        payload = {
            'username': 'testuser1',
            'password': 'testpass001',
            'email': 'test001@example.com',
            'first_name': 'test_f_name001',
            'last_name': 'test_l_name001',
        }

        create_user(**payload)
        response = self.client.post('/api/createuser/', payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_missing_password_field_error(self):
        """Test an error returned if password is missing from post data"""
        payload = {
            'username': 'testuser1',
            'email': 'test001@example.com',
            'first_name': 'test_f_name001',
            'last_name': 'test_l_name001',
        }

        response = self.client.post('/api/createuser/', payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_missing_username_field_error(self):
        """Test an error returned if password is missing from post data"""
        payload = {
            'password': 'testpass123',
            'email': 'test001@example.com',
            'first_name': 'test_f_name001',
            'last_name': 'test_l_name001',
        }

        response = self.client.post('/api/createuser/', payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""

        user_details = {
            'username': 'testuser1',
            'password': 'testpass001',
            'email': 'test001@example.com',
            'first_name': 'test_f_name001',
            'last_name': 'test_l_name001',
        }

        create_user(**user_details)

        payload = {
            'username': user_details['username'],
            'password': user_details['password'],
        }

        response = self.client.post('/api/token/', payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test generates token for valid credentials."""

        user_details = {
            'username': 'testuser1',
            'password': 'testpass001',
            'email': 'test001@example.com',
            'first_name': 'test_f_name001',
            'last_name': 'test_l_name001',
        }

        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': 'wrongpass',
        }

        response = self.client.post('/api/token/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication required for users."""

        response = self.client.get('/api/me/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='First Name',
            last_name='Last Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieve profile for logged in user."""

        response = self.client.get('/api/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)


    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""

        response = self.client.post('/api/me/', {})

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {'password': 'newpassword123'}

        response = self.client.patch('/api/me/', payload)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
