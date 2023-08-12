from django.contrib.auth import get_user_model


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

from users.serializers import UserSerializer, AuthTokenSerializer, ProfileSerializer, VerifyEmailSerializer
from users import models

class CreateUserView(CreateAPIView):

    model = get_user_model()
    permission_classes = [
        permissions.AllowAny  # Or anon users can't register
    ]
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        profile = models.Profile.objects.get(user=user.pk)
        if profile.is_email_verified == False:
            return Response(
                {'detail':'user email must be confirmed'},
                status=status.HTTP_403_FORBIDDEN)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


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

    def list(self, *args, **kwargs):
        self.serializer_class = ProfileSerializer
        return viewsets.ModelViewSet.list(self, *args, **kwargs)
    

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
                    {'detail':f'No user found for {data.get("email")}'},
                    status=status.HTTP_400_BAD_REQUEST)
        profile = models.Profile.objects.filter(user=user.pk).first()
        if profile.otp != data.get('otp'):

            return Response(
                    {'detail':'Incorrect otp'},
                    status=status.HTTP_400_BAD_REQUEST)
        elif profile.otp == data.get('otp'):
            profile.is_email_verified = True
            profile.save()
            return Response(
                    {'detail':'Your email has been verfied. You can now login.'},
                    status=status.HTTP_200_OK)
