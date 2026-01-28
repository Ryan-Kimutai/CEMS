from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

from .serializers import UserSignupSerializer, UserLoginSerializer, UserSerializer

User = get_user_model()


class SignupView(APIView):
    """
    POST /api/auth/signup/
    Create a new user account.
    """
    permission_classes = [AllowAny]  # Anyone can signup (no auth required)
    
    def post(self, request):
        """
        Handle POST request for user registration.
        
        Expected JSON body:
        {
            "email": "user@example.com",
            "username": "johndoe",
            "password": "securepassword123",
            "password2": "securepassword123"
        }
        """
        serializer = UserSignupSerializer(data=request.data)
        
        # Validate the data
        if serializer.is_valid():
            # Create the user (password is automatically hashed)
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Return success response
            return Response({
                'message': 'User created successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        # Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Step 1: Validate input data
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Step 2: Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # User doesn't exist - return generic error for security
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Step 3: Verify password
        # user.check_password() compares plain text password with hashed password
        if not user.check_password(password):
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Step 4: Check if user account is active
        if not user.is_active:
            return Response({
                'error': 'User account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Step 5: Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Blacklist the refresh token (optional, for extra security).
    """
    def post(self, request):
        """
        For now, just return success.
        Token expiration is handled client-side by deleting the token.
        
        In production, you might want to blacklist tokens.
        """
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
