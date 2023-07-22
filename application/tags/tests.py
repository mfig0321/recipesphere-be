from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from tags.models import Tag
from tags.serializers import TagSerializer
from tags.views import TagViewSet


def create_user(**params):
    """Create and return a new user."""

    return get_user_model().objects.create_user(**params)


class TagModelTest(TestCase):

    def test_create_recipe(self):
        """Test creating a recipe is successfull"""

        user = create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='First Name',
                last_name='Last Name'
        )
        tag = Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)


class PublicRecipeApiTest(TestCase):
    """Test Recipe Api endpoint"""
    def setUp(self):
        self.client = APIRequestFactory()

    def test_auth_required(self):
        """Test auth is required to call API"""
        view = TagViewSet.as_view({'get': 'list'})
        request = self.client.get('/api/tags/')
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
        self.view = TagViewSet.as_view({'get': 'list'})
        self.request = self.client.get('/api/tags/')
        force_authenticate(self.request, user=self.user)

    def test_retrive_recipes(self):
        """Test list of recipes"""
        Tag.objects.create(user=self.user, name='Dessert')
        Tag.objects.create(user=self.user, name='Vegan')

        response = self.view(self.request)
        recipes = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(recipes, many=True)

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

        Tag.objects.create(user=self.user, name='Dessert')
        Tag.objects.create(user=other_user, name='Vegan')

        response = self.view(self.request)
        tags = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class PrivateRecipeApiPatchTest(TestCase):
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
        self.view = TagViewSet.as_view({'patch': 'partial_update'})

    def test_update_tag(self):
        """Test updating tag."""
        tag = Tag.objects.create(user=self.user, name='After-Dinner')
        payload = {'name': 'Dessert'}
        request = self.client.patch('/api/tags/', payload)
        force_authenticate(request, user=self.user)
        
        response = self.view(request, pk=tag.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])


class PrivateRecipeApiDeleteTest(TestCase):
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
        self.view = TagViewSet.as_view({'delete': 'destroy'})

    def test_delete_tag(self):
        """Test deleting tag."""
        tag = Tag.objects.create(user=self.user, name='After-Dinner')
        request = self.client.delete('/api/tags/')
        force_authenticate(request, user=self.user)
        
        response = self.view(request, pk=tag.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())
