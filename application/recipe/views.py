from rest_framework import viewsets, response, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.http import FileResponse
from django.core.mail import EmailMessage
from drf_spectacular.utils import(
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from recipe.models import Recipe
from recipe import serializers

from tags.models import Tag
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def insert_newlines(string, every):
    lines = []
    for i in range(0, len(string), every):
        lines.append(string[i:i+every])
    return '\n'.join(lines)


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

    @action(detail=True, methods=['post'])
    def download(self, request, **kwargs):
        recipe = Recipe.objects.filter(id=kwargs.get('pk')).first()
        if recipe is None:
            return response.Response(
                {'detail':'No Recipe found.'},
                status=status.HTTP_204_NO_CONTENT
            )
        file_name = recipe.title.replace(" ", "-")
        file_name = file_name + '.pdf'
        buffer = io.BytesIO()
        w, h = A4
        c = canvas.Canvas(buffer)
        text = c.beginText(50, h - 50)
        text.setFont("Times-Roman", 24)
        text.textLine(recipe.title)
        c.drawText(text)
        c.drawImage(recipe.image.url,50, h - 210, width=150, height=150)
        text = c.beginText(50, h - 250)
        text.setFont("Times-Roman",16)
        text.textLines(f'Description: {insert_newlines(recipe.description, 70)}')
        text.textLine(f'Time to cook: {recipe.time_minutes} minutes.')
        text.textLine('Ingredients:')
        text.setFont("Times-Roman",12)
        for item in recipe.ingredients:
                value = recipe.ingredients[item]
                text.textLine(f'-{value}')
        text.setFont("Times-Roman",16)
        text.textLine('Instructions:')
        text.setFont("Times-Roman",12)
        text.textLines(f'{insert_newlines(recipe.instructions,100)}')
        c.drawText(text)
        
        c.showPage()
        c.save()
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True, filename=file_name)

    @action(detail=True, methods=['post'])
    def share(self, request, **kwargs):
        email = request.data.get('email')
        if email is None:
            return response.Response(
                {'detail': 'email field must be present'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = Recipe.objects.filter(id=kwargs.get('pk')).first()
        if recipe is None:
            return response.Response(
                {'detail':'No Recipe found.'},
                status=status.HTTP_204_NO_CONTENT
            )
        file_name = recipe.title.replace(" ", "-")
        file_name = file_name + '.pdf'
        buffer = io.BytesIO()
        w, h = A4
        c = canvas.Canvas(buffer)
        text = c.beginText(50, h - 50)
        text.setFont("Times-Roman", 24)
        text.textLine(recipe.title)
        c.drawText(text)
        c.drawImage(recipe.image.url,50, h - 210, width=150, height=150)
        text = c.beginText(50, h - 250)
        text.setFont("Times-Roman",16)
        text.textLines(f'Description: {insert_newlines(recipe.description,70)}')
        text.textLine(f'Time to cook: {recipe.time_minutes} minutes.')
        text.textLine('Ingredients:')
        text.setFont("Times-Roman",12)
        for item in recipe.ingredients:
                value = recipe.ingredients[item]
                text.textLine(f'-{value}')
        text.setFont("Times-Roman",16)
        text.textLine('Instructions:')
        text.setFont("Times-Roman",12)
        text.textLines(f'{insert_newlines(recipe.instructions,100)}')
        c.drawText(text)
        
        c.showPage()
        c.save()
        pdf = buffer.getvalue()
        buffer.close
        EmailMsg = EmailMessage(
            recipe.title,
            None,
            request.user.email,
            [f'{request.data.get("email")}'],
            None,
            headers={'Reply-To':f'{request.user.email}'}
        )
        EmailMsg.attach(file_name, pdf, 'application/pdf')
        EmailMsg.send()

        return response.Response({'detail': f'recipe sent to {request.data.get("email")}.'})

    @action(detail=False, methods=['get'])
    def my_recipes(self, request, **kwargs):
        recipes = Recipe.objects.filter(user=request.user)
        serializer =  serializers.RecipeSerializer(recipes, many=True)
        return response.Response(serializer.data)