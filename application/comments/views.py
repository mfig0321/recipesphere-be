from rest_framework import viewsets, response, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from comments import models, serializers
from recipe.models import Recipe
# Create your views here.


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    queryset = models.Comment.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        recipe = self.request.query_params.get('recipe')
        queryset = self.queryset

        if recipe:
            queryset = queryset.filter(recipe=recipe)

        return queryset.order_by('-id').distinct()
    
    def perform_create(self, serialzer):
        """Create new recipe."""
        serialzer.save(user=self.request.user)

    def destroy(self, *args, **kwargs):
        comment = models.Comment.objects.filter(id=kwargs.get('pk')).first()
        if comment.user != self.request.user:
            return response.Response(
                {'detail':'Not owner of comment. Can not delete comment.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return viewsets.ModelViewSet.destroy(self, *args, **kwargs)