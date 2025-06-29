from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'city', 'state', 'country', 'postal_code']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name', 'profile']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password')
        password_confirm = validated_data.pop('password_confirm', None)  # Remove password_confirm field

        # Set username to email
        email = validated_data.get('email')
        validated_data['username'] = email

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Create user profile
        if profile_data:
            UserProfile.objects.create(user=user, **profile_data)
        else:
            UserProfile.objects.create(user=user)

        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that accepts email instead of username
    """
    username_field = 'email'

    def validate(self, attrs):
        # The authenticate call simply passes username and password along
        # Get the email value and use it as the username
        email = attrs.get('email')

        # Create a new dictionary with 'username' set to the email value
        authentication_kwargs = {
            'username': email,
            'password': attrs.get('password')
        }

        # Use Django's authenticate function directly
        from django.contrib.auth import authenticate
        self.user = authenticate(request=self.context.get('request'), **authentication_kwargs)

        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )

        # Get the token for the user
        refresh = self.get_token(self.user)

        # Return the token
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
