""""
Serializers for recipe APIs
"""

from rest_framework import serializers

from recipe.models import Recipe
from tags.serializers import TagSerializer


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ['id',
                  'title',
                  'description',
                  'image',
                  'time_minutes',
                  'ingredients',
                  'instructions',
                  'tags'
                  ]
        read_only_fields = ['id']

