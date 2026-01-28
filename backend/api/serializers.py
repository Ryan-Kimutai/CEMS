from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event, SavedEvent
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

#User serializer classes

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

# Event serializer classes

class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for Event model.
    Shows event details including creator info.
    """
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    creator_email = serializers.CharField(source='creator.email', read_only=True)
    is_saved = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'date',
            'location',
            'creator',
            'creator_name',
            'creator_email',
            'is_approved',
            'is_saved',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at', 'is_approved']
    
    def get_is_saved(self, obj):
        """
        Check if current user has saved this event.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedEvent.objects.filter(
                user=request.user,
                event=obj
            ).exists()
        return False


class EventCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating events.
    Simpler - only needs basic fields.
    """
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location']
    
    def create(self, validated_data):
        """
        Create event with the authenticated user as creator.
        Events start as not approved.
        """
        request = self.context.get('request')
        validated_data['creator'] = request.user
        validated_data['is_approved'] = False  # Needs admin approval
        return super().create(validated_data)


class SavedEventSerializer(serializers.ModelSerializer):
    """
    Serializer for saved events.
    """
    event = EventSerializer(read_only=True)
    
    class Meta:
        model = SavedEvent
        fields = ['id', 'event', 'saved_at']
        read_only_fields = ['id', 'saved_at']