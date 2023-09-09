from django.contrib.auth import get_user_model

from django.core.mail import send_mail
from django.contrib.auth.models import User
from rest_framework import (authentication,
                            permissions,
                            views,
                            viewsets,
                            response,
                            status,)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from users.serializers import (UserSerializer,
                               AuthTokenSerializer,
                               ProfileSerializer,
                               VerifyEmailSerializer,
                               ResendOtpSerializer)
from users import models
from recipe import models as recipe_models

class CreateUserView(CreateAPIView):

    model = get_user_model()
    permission_classes = [
        permissions.AllowAny  # Or anon users can't register
    ]
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response({
                'detail':'User Created',
                'status': 201}, status=201)
        else:
            errors_parsed = serializer.errors
            errors_parsed['status'] = 400
            return Response(errors_parsed, status=status.HTTP_400_BAD_REQUEST)


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if (serializer.is_valid()):

            user = serializer.validated_data['user']
            profile = models.Profile.objects.get(user=user.pk)
            if profile.is_email_verified == False:
                return Response(
                    {'detail':'user email must be confirmed','status':403},
                    status=status.HTTP_403_FORBIDDEN)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email,
                'status': 200
            })
        else:
            errors_parsed = serializer.errors
            errors_parsed['status'] = 400
            print(errors_parsed)
            return response.Response(
                errors_parsed,
                status=400,
            )


class ManageUserView(RetrieveUpdateAPIView):
    """Manage the authenticated user."""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and Return the authenticated user."""
        return self.request.user


class ProfileViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = ProfileSerializer
    queryset = models.Profile.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        obj = models.Profile.objects.filter(user=request.user).first()
        serializer = ProfileSerializer(obj)
        data = serializer.data
        data['status'] = 200
        return response.Response(
            data
        )
    
    @action(detail=False, methods=['post'])
    def add_favorite(self, request, **kwargs):
        recipe = recipe_models.Recipe.objects.filter(id=request.data.get('recipe')).first()
        profile = models.Profile.objects.filter(user=self.request.user.pk).first()
        profile.favorites.add(recipe)

        return response.Response({
            "detail":"Favorite added",
            "status": 200
        })

    @action(detail=False, methods=['post'])
    def remove_favorite(self, request, **kwargs):
        recipe = recipe_models.Recipe.objects.filter(id=request.data.get('recipe')).first()
        profile = models.Profile.objects.filter(user=self.request.user.pk).first()
        profile.favorites.remove(recipe)

        return response.Response({
            "detail":"Favorite removed",
            "status": 200
            }
        )

class VerifyEmailView(views.APIView):
    permission_classes = [
        permissions.AllowAny  # Or anon users can't register
    ]
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        data = request.data
        user = User.objects.filter(email=data.get('email')).first()
        if user is None:
            return Response(
                    {
                        'detail':f'No user found for {data.get("email")}',
                        'status': 400
                    },
                    status=status.HTTP_400_BAD_REQUEST)
        profile = models.Profile.objects.filter(user=user.pk).first()
        if profile.otp != data.get('otp'):

            return Response(
                    {'detail':'Incorrect otp','status': 400},
                    status=status.HTTP_400_BAD_REQUEST)
        elif profile.otp == data.get('otp'):
            profile.is_email_verified = True
            profile.save()
            return Response(
                    {'detail':'Your email has been verfied. You can now login.','status':200},
                    status=status.HTTP_200_OK)


class ResendOtpView(views.APIView):
    permission_classes = [
        permissions.AllowAny  # Or anon users can't register
    ]
    serializer_class = ResendOtpSerializer

    def post(self, request):
        data = request.data
        user = User.objects.filter(email=data.get('email')).first()
        if user is None:
            return Response(
                    {'detail':f'No user found for {data.get("email")}'},
                    status=status.HTTP_400_BAD_REQUEST)
        profile = models.Profile.objects.filter(user=user.pk).first()
        send_mail(
            'RecipeSphere One-time Password',
            f'Your one time password is {profile.otp}.',
            'michael.figueroa73@gmail.com',
            [f'{user.email}']
        )
        return Response(
                {'detail':'Your OTP has been resnt'},
                status=status.HTTP_200_OK)