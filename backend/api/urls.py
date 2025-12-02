from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/login', views.auth_login, name='auth_login'),
    path('auth/logout', views.auth_logout, name='auth_logout'),
    
    # Time
    path('time', views.get_server_time, name='get_server_time'),
    
    # User
    path('user', views.user_detail, name='user_detail'),
    path('user/location', views.user_location, name='user_location'),
    
    # Calendar Types
    path('calendar-types', views.calendar_types_list, name='calendar_types_list'),
    path('calendar-types/<str:type_id>', views.calendar_type_detail, name='calendar_type_detail'),
    path('calendar-types/<str:type_id>/visibility', views.calendar_type_visibility, name='calendar_type_visibility'),
    
    # Events
    path('events', views.events_list, name='events_list'),
    path('events/<uuid:event_id>', views.event_detail, name='event_detail'),
    path('events/<uuid:event_id>/complete', views.event_complete, name='event_complete'),
    path('events/<uuid:event_id>/links', views.event_links, name='event_links'),
    
    # Files
    path('files/upload', views.file_upload, name='file_upload'),
    path('files/<uuid:file_id>', views.file_delete, name='file_delete'),
    
    # Reminders (Placeholder)
    path('reminders', views.reminders_list, name='reminders_list'),
    
    # Commute (Placeholder)
    path('location/commute', views.location_commute, name='location_commute'),
    
    # Agent API - 为AI Agent提供接口
    path('agent/info', views.agent_info, name='agent_info'),
    path('agent/action', views.agent_action, name='agent_action'),
    
    # Agent AI Endpoints - 供前端调用，对接外部AI Agent
    path('agent/reminder-context', views.agent_reminder_context, name='agent_reminder_context'),
    path('agent/parse-task', views.agent_parse_task, name='agent_parse_task'),
    path('agent/parse-calendar-type', views.agent_parse_calendar_type, name='agent_parse_calendar_type'),
    path('agent/parse-event', views.agent_parse_event, name='agent_parse_event'),
    path('agent/generate-reminders', views.agent_generate_reminders, name='agent_generate_reminders'),
]

