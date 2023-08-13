from rest_framework import viewsets, response, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from drf_spectacular.utils import(
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from recipe.models import Recipe
from recipe import serializers

from tags.models import Tag


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma seperated list of Tag Ids to filter'
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        tags = self.request.query_params.get('tags')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        return queryset.order_by('-id').distinct()

    def list(self, *args, **kwargs):
        self.serializer_class = serializers.RecipeSerializer
        return viewsets.ModelViewSet.list(self, *args, **kwargs)

    def retrieve(self, *args, **kwargs):
        self.serializer_class = serializers.RecipeSerializer
        return viewsets.ModelViewSet.retrieve(self, *args, **kwargs)

    def perform_create(self, serialzer):
        """Create new recipe."""
        serialzer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_tag(self, request, **kwargs):
        tag = Tag.objects.filter(name=request.data.get('tag')).first()
        if tag is None:
            tag = Tag.objects.create(name=request.data.get('tag'))
        recipe = Recipe.objects.filter(id=kwargs.get('pk')).first()
        recipe.tags.add(tag)

        return response.Response({"detail":"Tag added"})


    @action(detail=True, methods=['post'])
    def remove_tag(self, request, **kwargs):
        tag = Tag.objects.filter(name=request.data.get('tag')).first()
        if tag is None:
            return response.Response(
                {'detail':'tag does not exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = Recipe.objects.filter(id=kwargs.get('pk')).first()
        recipe.tags.remove(tag)

        return response.Response({"detail":"Tag removed"})