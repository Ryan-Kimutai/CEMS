from django.contrib import admin
from .models import User, Event, SavedEvent

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_admin', 'is_staff', 'date_joined')
    list_filter = ('is_admin', 'is_staff', 'date_joined')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'date', 'location', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at', 'date')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-date',)

@admin.register(SavedEvent)
class SavedEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__email', 'event__title')
    readonly_fields = ('saved_at',)
