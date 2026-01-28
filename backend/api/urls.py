from django.urls import path
from .views import (
    # Auth views
    SignupView,
    LoginView,
    LogoutView,
    # Event views
    EventListView,
    EventCreateView,
    EventDetailView,
    EventDeleteView,
    EventApproveView,
    # Saved events views
    SavedEventListView,
    SavedEventToggleView,
)

urlpatterns = [
    # Authentication endpoints
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    
    # Event endpoints
    path('events/', EventListView.as_view(), name='event-list'),
    path('events/create/', EventCreateView.as_view(), name='event-create'),
    path('events/<int:event_id>/', EventDetailView.as_view(), name='event-detail'),
    path('events/<int:event_id>/delete/', EventDeleteView.as_view(), name='event-delete'),
    path('events/<int:event_id>/approve/', EventApproveView.as_view(), name='event-approve'),
    
    # Saved events endpoints
    path('saved-events/', SavedEventListView.as_view(), name='saved-events-list'),
    path('saved-events/<int:event_id>/toggle/', SavedEventToggleView.as_view(), name='saved-event-toggle'),
]