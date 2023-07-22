""""
Serializers for recipe APIs
"""

from rest_framework import serializers

from tags.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
