from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from recipe.models import Recipe
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer
    )
from recipe.views import RecipeViewSet


def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample Recipe Title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample Description',
        'link': 'http://example.com/recipe.pdf',
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
        recipe = Recipe.objects.create(
            user=user,
            title='Sample Recipe Name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample Recipe Description',
        )

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

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to auth user"""

        other_user = get_user_model().objects.create(
            username='testuser2',
            password='testpass002',
            email='test002@example.com',
            first_name='test_f_name002',
            last_name='test_l_name002',
        )

        create_recipe(user=self.user)
        create_recipe(user=other_user)

        response = self.view(self.request)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)

        request = self.client.get('/api/recipes')
        force_authenticate(request, self.user)
        view = RecipeViewSet.as_view({'get': 'retrieve'})
        response = response = view(request, pk=recipe.id)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe"""
        
        payload = {
            'title': 'sample rec3ipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }

        request = self.client.post('/api/recipes', payload)
        force_authenticate(request, self.user)
        view = RecipeViewSet.as_view({'post': 'create'})
        response = response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data.get('id'))

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
