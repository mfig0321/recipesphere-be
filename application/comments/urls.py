"""
URL mappings for the recipe app
"""

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from comments import views

router = DefaultRouter()
router.register('api/comments', views.CommentViewSet)

app_name = 'comments'

urlpatterns = [
    path('', include(router.urls))
]