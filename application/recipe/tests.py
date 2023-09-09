from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from recipe.models import Recipe
from recipe.serializers import (
    RecipeSerializer,
    )
from recipe.views import RecipeViewSet
import json

def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample Recipe Title',
        'time_minutes': 22,
        'description': 'Sample Description',
        'instructions': 'boil for 10 minutes',
        'ingredients': {'1':'eggs'}
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)

    return recipe


def create_user(**params):
    """Create and return a new user."""

    return get_user_model().objects.create_user(**params)


class RecipeModelTest(TestCase):

    def test_create_recipe(self):
        """Test creating a recipe is successfull"""

        user = create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='First Name',
                last_name='Last Name'
        )
        recipe = create_recipe(user)

        self.assertEqual(str(recipe), recipe.title)


class PublicRecipeApiTest(TestCase):
    """Test Recipe Api endpoint"""
    def setUp(self):
        self.client = APIRequestFactory()

    def test_auth_required(self):
        """Test auth is required to call API"""
        view = RecipeViewSet.as_view({'get': 'list'})
        request = self.client.get('/api/recipes/')
        response = view(request)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
            )


class PrivateRecipeApiTest(TestCase):
    """Test Authenticated API request"""

    def setUp(self):
        self.client = APIRequestFactory()
        self.user = get_user_model().objects.create(
            username='testuser1',
            password='testpass001',
            email='test001@example.com',
            first_name='test_f_name001',
            last_name='test_l_name001',
        )
        self.view = RecipeViewSet.as_view({'get': 'list'})
        self.request = self.client.get('/api/recipes/')
        force_authenticate(self.request, user=self.user)

    def test_retrive_recipes(self):
        """Test list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response = self.view(self.request)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    