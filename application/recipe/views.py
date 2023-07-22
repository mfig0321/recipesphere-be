from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for auth user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def list(self, *args, **kwargs):
        self.serializer_class = serializers.RecipeSerializer
        return viewsets.ModelViewSet.list(self, *args, **kwargs)

    def retrieve(self, *args, **kwargs):
        self.serializer_class = serializers.RecipeDetailSerializer
        return viewsets.ModelViewSet.retrieve(self, *args, **kwargs)

    def perform_create(self, serialzer):
        """Create new recipe."""
        serialzer.save(user=self.request.user)
