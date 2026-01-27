from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model extending Django's built-in User.
    Like a 'users' table in your database.
    """
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    
    # Use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email


class Event(models.Model):
    """
    Event model - represents events in your system.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=300)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']  # Show newest first
    
    def __str__(self):
        return self.title


class SavedEvent(models.Model):
    """
    Represents a user saving an event (many-to-many relationship).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_events')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'event']  # User can only save an event once
    
    def __str__(self):
        return f"{self.user.email} saved {self.event.title}"
