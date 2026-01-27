from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSignupSerializer(serializers.ModelSerializer):
    """
    Handles user registration/signup.
    Think of this like validation middleware in Express.js
    """
    password = serializers.CharField(
        write_only=True,  # Don't send password back in response
        required=True,
        validators=[validate_password]  # Django's built-in password validation
    )
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2']
    
    def validate(self, attrs):
        """
        Custom validation - check if passwords match.
        This runs automatically before creating the user.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create and return a new user with encrypted password.
        Django automatically hashes the password with create_user().
        """
        # Remove password2 since we don't need it in the database
        validated_data.pop('password2')
        
        # Create user with hashed password
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Handles user login validation.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """
    Return user data (without password).
    Used in responses after login/signup.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_admin']
        read_only_fields = ['id']