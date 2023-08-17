from django.shortcuts import render

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from tags.models import Tag
from tags import serializers

# Create your views here.


class TagViewSet(viewsets.ModelViewSet):
    """Manage tags in the database"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        name = self.request.query_params.get('name')
        queryset = self.queryset
        if name:
            
            queryset = queryset.filter(name=name)

        return queryset.order_by('-id').distinct()
