from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import (
    UserSignupSerializer, UserLoginSerializer, UserSerializer,
    EventSerializer, EventCreateSerializer, SavedEventSerializer
)
from .models import Event, SavedEvent

User = get_user_model()


# ==================== AUTHENTICATION VIEWS ====================
# (Keep your existing SignupView, LoginView, LogoutView here)

class SignupView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'User created successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'error': 'User account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
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
    def post(self, request):
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)


# ==================== EVENT VIEWS ====================

class EventListView(APIView):
    """
    GET /api/events/
    
    List all approved events.
    Anyone can view (no authentication required).
    
    Query parameters:
    - show_all=true (admin only) - shows all events including unapproved
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Check if user wants to see all events (admin only)
        show_all = request.query_params.get('show_all', 'false').lower() == 'true'
        
        if show_all and request.user.is_authenticated and request.user.is_admin:
            # Admin can see all events
            events = Event.objects.all()
        else:
            # Regular users only see approved events
            events = Event.objects.filter(is_approved=True)
        
        serializer = EventSerializer(
            events,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'events': serializer.data,
            'count': events.count()
        }, status=status.HTTP_200_OK)


class EventCreateView(APIView):
    """
    POST /api/events/
    
    Create a new event.
    Requires authentication.
    Event starts as unapproved (needs admin approval).
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = EventCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            event = serializer.save()
            
            return Response({
                'message': 'Event created successfully. Waiting for admin approval.',
                'event': EventSerializer(event, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventDetailView(APIView):
    """
    GET /api/events/<id>/
    
    Get details of a specific event.
    Anyone can view approved events.
    Creators and admins can view their own unapproved events.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        
        # Check permissions
        if not event.is_approved:
            if not request.user.is_authenticated:
                return Response({
                    'error': 'Event not found or not approved'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Only creator or admin can see unapproved events
            if event.creator != request.user and not request.user.is_admin:
                return Response({
                    'error': 'Event not found or not approved'
                }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EventSerializer(event, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventDeleteView(APIView):
    """
    DELETE /api/events/<id>/
    
    Delete an event.
    Only event creator or admin can delete.
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)

        print("creator:", event.creator.id, "request:", request.user.id)
        # Check if user is creator or admin
        if event.creator != request.user and not request.user.is_admin:
            return Response({
                'error': 'You do not have permission to delete this event'
            }, status=status.HTTP_403_FORBIDDEN)
        
        event_title = event.title
        event.delete()
        
        return Response({
            'message': f'Event "{event_title}" deleted successfully'
        }, status=status.HTTP_200_OK)


class EventApproveView(APIView):
    """
    PATCH /api/events/<id>/approve/
    
    Approve or reject an event.
    Only admins can approve.
    
    Body: { "is_approved": true/false }
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, event_id):
        # Check if user is admin
        if not request.user.is_admin:
            return Response({
                'error': 'Only admins can approve events'
            }, status=status.HTTP_403_FORBIDDEN)
        
        event = get_object_or_404(Event, id=event_id)
        
        is_approved = request.data.get('is_approved')
        if is_approved is None:
            return Response({
                'error': 'is_approved field is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        event.is_approved = is_approved
        event.save()
        
        status_text = 'approved' if is_approved else 'rejected'
        
        return Response({
            'message': f'Event "{event.title}" {status_text}',
            'event': EventSerializer(event, context={'request': request}).data
        }, status=status.HTTP_200_OK)


# ==================== SAVED EVENTS VIEWS ====================

class SavedEventListView(APIView):
    """
    GET /api/saved-events/
    
    Get all events saved by the current user.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        saved_events = SavedEvent.objects.filter(user=request.user)
        serializer = SavedEventSerializer(saved_events, many=True)
        
        return Response({
            'saved_events': serializer.data,
            'count': saved_events.count()
        }, status=status.HTTP_200_OK)


class SavedEventToggleView(APIView):
    """
    POST /api/saved-events/<event_id>/toggle/
    
    Toggle save/unsave an event.
    If event is saved, unsave it.
    If event is not saved, save it.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        
        # Check if event is approved
        if not event.is_approved:
            return Response({
                'error': 'Cannot save unapproved events'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already saved
        saved_event = SavedEvent.objects.filter(
            user=request.user,
            event=event
        ).first()
        
        if saved_event:
            # Unsave
            saved_event.delete()
            return Response({
                'message': f'Event "{event.title}" removed from saved events',
                'is_saved': False
            }, status=status.HTTP_200_OK)
        else:
            # Save
            SavedEvent.objects.create(
                user=request.user,
                event=event
            )
            return Response({
                'message': f'Event "{event.title}" saved successfully',
                'is_saved': True
            }, status=status.HTTP_201_CREATED)