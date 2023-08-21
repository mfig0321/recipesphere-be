""""
Serializers for recipe APIs
"""

from rest_framework import serializers
from comments import models
from users import serializers as users_serializer

class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments."""

    user = users_serializer.UserSerializer(required=False)

    class Meta:
        model = models.Comment
        fields = ['id',
                  'user',
                  'recipe',
                  'text',
                  'created_at',
                  ]
        read_only_fields = ['id']

