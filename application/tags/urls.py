"""
URL mappings for the recipe app
"""

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from tags import views

router = DefaultRouter()
router.register('api/tags', views.TagViewSet)

app_name = 'tags'

urlpatterns = [
    path('', include(router.urls))
]