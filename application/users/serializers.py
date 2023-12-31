
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.core.mail import send_mail

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from recipe import serializers as recipe_serializer
from users import models
from random import randint
UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=UserModel.objects.all())]
    )

    class Meta:
        model = UserModel
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        """Create and return a user."""
        user = UserModel.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()
        otp = str(randint(100000, 999999))
        send_mail(
            'RecipeSphere One-time Password',
            f'Your one time password is {otp}.',
            'michael.figueroa73@gmail.com',
            [f'{user.email}']
        )
        models.Profile.objects.create(user=user, otp=otp)
        user.password = ''

        return user

    def update(self, instance, validated_data):
        """Update and return user"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        user.password = ''

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user auth toke"""
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )
        if not user:
            msg = 'Unable to authenticate with provicded credentials'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    favorites = recipe_serializer.RecipeSerializer(many=True)

    class Meta:
        model= models.Profile
        fields = "__all__"


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
