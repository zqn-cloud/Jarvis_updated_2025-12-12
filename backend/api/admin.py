from django.contrib import admin
from .models import User, UserLocation, AccessToken, CalendarType, Event, EventLink, UploadedFile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['account_id', 'home_address', 'school_address', 'created_at']
    search_fields = ['account_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ['user', 'latitude', 'longitude', 'accuracy', 'timestamp']
    list_filter = ['user']
    readonly_fields = ['id', 'timestamp']


@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'is_active', 'created_at', 'expires_at']
    list_filter = ['is_active', 'user']
    readonly_fields = ['id', 'created_at']


@admin.register(CalendarType)
class CalendarTypeAdmin(admin.ModelAdmin):
    list_display = ['user', 'type_id', 'name', 'color', 'is_visible', 'is_deletable']
    list_filter = ['user', 'is_visible', 'is_deletable']
    search_fields = ['name', 'user__account_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'date', 'is_all_day', 'start_time', 'completed', 'calendar_type']
    list_filter = ['user', 'date', 'completed', 'is_all_day', 'calendar_type']
    search_fields = ['title', 'user__account_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'date'


@admin.register(EventLink)
class EventLinkAdmin(admin.ModelAdmin):
    list_display = ['event', 'url', 'created_at']
    search_fields = ['event__title', 'url']
    readonly_fields = ['id', 'created_at']


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['user', 'original_name', 'size', 'mime_type', 'created_at']
    list_filter = ['user', 'mime_type']
    search_fields = ['original_name', 'user__account_id']
    readonly_fields = ['id', 'created_at']
