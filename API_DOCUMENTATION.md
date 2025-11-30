# Jarvis Calendar - Backend API Documentation

## Overview

This document provides comprehensive API specifications for the Jarvis Calendar application backend. The API follows RESTful conventions and uses JSON for request/response bodies.

## Base Configuration

```
Base URL: https://api.jarvis-calendar.com/v1
Content-Type: application/json
Authorization: Bearer <token>
```

## Authentication

### POST /auth/login
Login with credentials.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
    "expires_in": 3600,
    "user": {
      "id": "user_123",
      "name": "John Doe",
      "email": "user@example.com",
      "avatar": "https://example.com/avatar.jpg"
    }
  }
}
```

### POST /auth/register
Register a new user.

**Request:**
```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "password123"
}
```

### POST /auth/refresh
Refresh access token.

**Request:**
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

### POST /auth/logout
Logout and invalidate token.

---

## Events (Tasks/Events)

### GET /events
Get all events with optional filters.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| date | string | Filter by specific date (YYYY-MM-DD) |
| start_date | string | Range start date (YYYY-MM-DD) |
| end_date | string | Range end date (YYYY-MM-DD) |
| type_id | string | Filter by calendar type ID |
| completed | boolean | Filter by completion status |
| page | integer | Page number (default: 1) |
| limit | integer | Items per page (default: 50) |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "id": "evt_001",
        "title": "Team Meeting",
        "date": "2025-11-30",
        "is_all_day": false,
        "start_time": "10:00",
        "end_time": "11:00",
        "location": "Conference Room A",
        "description": "Weekly sync meeting",
        "type_id": "type_events",
        "color": "#F59E0B",
        "completed": false,
        "links": ["https://meet.google.com/abc-defg-hij"],
        "attachment": {
          "name": "agenda.pdf",
          "url": "https://storage.example.com/files/agenda.pdf",
          "size": 102400,
          "mime_type": "application/pdf"
        },
        "created_at": "2025-11-25T08:00:00Z",
        "updated_at": "2025-11-25T08:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 120,
      "total_pages": 3
    }
  }
}
```

### GET /events/:id
Get single event by ID.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "evt_001",
    "title": "Team Meeting",
    "date": "2025-11-30",
    "is_all_day": false,
    "start_time": "10:00",
    "end_time": "11:00",
    "location": "Conference Room A",
    "description": "Weekly sync meeting",
    "type_id": "type_events",
    "color": "#F59E0B",
    "completed": false,
    "links": ["https://meet.google.com/abc-defg-hij"],
    "attachment": null,
    "reminders": [
      { "type": "notification", "minutes_before": 15 },
      { "type": "email", "minutes_before": 60 }
    ],
    "created_at": "2025-11-25T08:00:00Z",
    "updated_at": "2025-11-25T08:00:00Z"
  }
}
```

### POST /events
Create a new event.

**Request:**
```json
{
  "title": "Doctor Appointment",
  "date": "2025-12-01",
  "is_all_day": false,
  "start_time": "14:00",
  "end_time": "15:00",
  "location": "City Hospital",
  "description": "Annual checkup",
  "type_id": "type_routine",
  "links": [],
  "attachment_id": null
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "evt_002",
    "title": "Doctor Appointment",
    "date": "2025-12-01",
    "is_all_day": false,
    "start_time": "14:00",
    "end_time": "15:00",
    "location": "City Hospital",
    "type_id": "type_routine",
    "color": "#EC4899",
    "completed": false,
    "created_at": "2025-11-30T10:00:00Z"
  }
}
```

### PUT /events/:id
Update an existing event.

**Request:**
```json
{
  "title": "Doctor Appointment - Updated",
  "start_time": "15:00",
  "end_time": "16:00",
  "completed": false,
  "links": ["https://hospital.com/appointment/123"]
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "evt_002",
    "title": "Doctor Appointment - Updated",
    "date": "2025-12-01",
    "start_time": "15:00",
    "end_time": "16:00",
    "updated_at": "2025-11-30T12:00:00Z"
  }
}
```

### PATCH /events/:id/complete
Toggle event completion status.

**Request:**
```json
{
  "completed": true
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "evt_002",
    "completed": true,
    "completed_at": "2025-11-30T14:00:00Z"
  }
}
```

### DELETE /events/:id
Delete an event.

**Response (200):**
```json
{
  "success": true,
  "message": "Event deleted successfully"
}
```

### POST /events/:id/links
Add a link to an event.

**Request:**
```json
{
  "url": "https://docs.google.com/document/d/123"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "links": [
      "https://meet.google.com/abc",
      "https://docs.google.com/document/d/123"
    ]
  }
}
```

### DELETE /events/:id/links
Remove a link from an event.

**Request:**
```json
{
  "url": "https://docs.google.com/document/d/123"
}
```

---

## Calendar Types (Categories)

### GET /calendar-types
Get all calendar types.

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "type_general",
      "name": "General",
      "color": "#6B7280",
      "is_visible": true,
      "is_default": true,
      "is_deletable": false,
      "event_count": 15,
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": "type_routine",
      "name": "Routine",
      "color": "#EC4899",
      "is_visible": true,
      "is_default": false,
      "is_deletable": true,
      "event_count": 8,
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": "type_events",
      "name": "Events",
      "color": "#F59E0B",
      "is_visible": true,
      "is_default": false,
      "is_deletable": true,
      "event_count": 12,
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": "type_holidays",
      "name": "Holidays",
      "color": "#3B82F6",
      "is_visible": true,
      "is_default": false,
      "is_deletable": true,
      "event_count": 5,
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": "type_school",
      "name": "School",
      "color": "#22C55E",
      "is_visible": true,
      "is_default": false,
      "is_deletable": true,
      "event_count": 20,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### POST /calendar-types
Create a new calendar type.

**Request:**
```json
{
  "name": "Fitness",
  "color": "#10B981"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "type_fitness",
    "name": "Fitness",
    "color": "#10B981",
    "is_visible": true,
    "is_default": false,
    "is_deletable": true,
    "event_count": 0,
    "created_at": "2025-11-30T10:00:00Z"
  }
}
```

### PUT /calendar-types/:id
Update a calendar type.

**Request:**
```json
{
  "name": "Workout",
  "color": "#059669"
}
```

### PATCH /calendar-types/:id/visibility
Toggle visibility.

**Request:**
```json
{
  "is_visible": false
}
```

### DELETE /calendar-types/:id
Delete a calendar type. All events of this type will be moved to "General".

**Response (200):**
```json
{
  "success": true,
  "message": "Calendar type deleted. 5 events moved to General.",
  "data": {
    "events_moved": 5
  }
}
```

---

## Reminders (Smart Suggestions)

### GET /reminders
Get smart reminders/suggestions for the user.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| date | string | Date for reminders (default: today) |
| types | string | Comma-separated types: weather,commute,birthday,deadline |

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "rem_weather",
      "type": "weather",
      "title": "今日天气",
      "subtitle": "多云转晴，18°C - 25°C，适合外出",
      "bg_color": "#EAF4FD",
      "icon_bg": "#60A5FA",
      "data": {
        "condition": "partly_cloudy",
        "temp_min": 18,
        "temp_max": 25,
        "humidity": 65,
        "wind_speed": 12
      },
      "action_url": null,
      "priority": 1
    },
    {
      "id": "rem_commute",
      "type": "commute",
      "title": "通勤信息",
      "subtitle": "前往学校约需 25 分钟，距离 8.5 公里",
      "bg_color": "#E8F5E9",
      "icon_bg": "#4ADE80",
      "data": {
        "destination": "School",
        "duration_minutes": 25,
        "distance_km": 8.5,
        "traffic_status": "normal"
      },
      "action_url": "https://maps.google.com/?q=...",
      "priority": 2
    },
    {
      "id": "rem_birthday",
      "type": "important",
      "title": "重要提醒",
      "subtitle": "明天是 Kai 的生日，记得准备礼物 🎁",
      "bg_color": "#FCE4EC",
      "icon_bg": "#F472B6",
      "data": {
        "event_id": "evt_001",
        "person_name": "Kai",
        "event_date": "2025-12-01"
      },
      "action_url": null,
      "priority": 1
    }
  ]
}
```

---

## AI Agent Integration

### POST /ai/parse-event
Parse natural language into event data.

**Request:**
```json
{
  "text": "Meeting with John tomorrow at 3pm at Starbucks for 1 hour",
  "context": {
    "current_date": "2025-11-30",
    "timezone": "Asia/Shanghai"
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "parsed": {
      "title": "Meeting with John",
      "date": "2025-12-01",
      "is_all_day": false,
      "start_time": "15:00",
      "end_time": "16:00",
      "location": "Starbucks",
      "type_id": null,
      "suggested_type": "type_events"
    },
    "confidence": 0.95,
    "alternatives": [
      {
        "title": "Meeting with John at Starbucks",
        "date": "2025-12-01",
        "start_time": "15:00",
        "end_time": "16:00"
      }
    ]
  }
}
```

### POST /ai/parse-calendar-type
Parse natural language to create calendar type.

**Request:**
```json
{
  "text": "Create a fitness category with green color for my workout schedule"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "parsed": {
      "name": "Fitness",
      "color": "#22C55E"
    },
    "confidence": 0.92
  }
}
```

### POST /ai/quick-add
Quickly add a task via natural language.

**Request:**
```json
{
  "text": "买牛奶回家的路上",
  "context": {
    "current_date": "2025-11-30",
    "timezone": "Asia/Shanghai"
  }
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "event": {
      "id": "evt_new_001",
      "title": "买牛奶",
      "date": "2025-11-30",
      "is_all_day": true,
      "type_id": "type_general",
      "color": "#6B7280",
      "completed": false
    },
    "message": "已添加任务：买牛奶"
  }
}
```

### POST /ai/suggest
Get AI suggestions based on context.

**Request:**
```json
{
  "context": {
    "current_date": "2025-11-30",
    "upcoming_events": ["evt_001", "evt_002"],
    "user_preferences": {
      "work_hours": { "start": "09:00", "end": "18:00" },
      "preferred_meeting_duration": 60
    }
  },
  "request_type": "schedule_optimization"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "type": "reschedule",
        "message": "建议将'Team Meeting'移到上午，下午有连续3个会议可能会疲劳",
        "action": {
          "event_id": "evt_001",
          "suggested_time": "10:00"
        }
      },
      {
        "type": "reminder",
        "message": "明天是Kai的生日，要不要现在设置一个买礼物的提醒？",
        "action": {
          "create_event": {
            "title": "买生日礼物",
            "date": "2025-11-30",
            "is_all_day": true
          }
        }
      }
    ]
  }
}
```

### GET /ai/agent/events
Agent-specific endpoint to read all events (for AI agent integration).

**Headers:**
```
Authorization: Bearer <agent_token>
X-Agent-ID: agent_jarvis_001
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | string | Start of date range |
| end_date | string | End of date range |
| include_completed | boolean | Include completed events |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user_id": "user_123",
    "events": [
      {
        "id": "evt_001",
        "title": "Team Meeting",
        "date": "2025-11-30",
        "start_time": "10:00",
        "end_time": "11:00",
        "type": "Events",
        "completed": false
      }
    ],
    "summary": {
      "total_events": 15,
      "completed": 5,
      "pending": 10,
      "today": 4,
      "this_week": 12
    }
  }
}
```

### POST /ai/agent/action
Agent performs action on behalf of user.

**Request:**
```json
{
  "agent_id": "agent_jarvis_001",
  "action": "create_event",
  "payload": {
    "title": "Reminder: Call Mom",
    "date": "2025-12-01",
    "is_all_day": true,
    "type_id": "type_general"
  },
  "reason": "User requested via voice command"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "action_id": "action_001",
    "result": {
      "event_id": "evt_new_002",
      "status": "created"
    }
  }
}
```

---

## File Upload

### POST /files/upload
Upload a file attachment.

**Request (multipart/form-data):**
```
file: <binary>
type: attachment
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "file_001",
    "name": "document.pdf",
    "url": "https://storage.example.com/files/document.pdf",
    "size": 102400,
    "mime_type": "application/pdf",
    "created_at": "2025-11-30T10:00:00Z"
  }
}
```

### DELETE /files/:id
Delete a file.

---

## User Settings

### GET /settings
Get user settings.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "profile": {
      "name": "John Doe",
      "email": "john@example.com",
      "avatar": "https://example.com/avatar.jpg"
    },
    "preferences": {
      "language": "en",
      "timezone": "Asia/Shanghai",
      "time_format": "12h",
      "week_start": "sunday",
      "theme": "light"
    },
    "notifications": {
      "push_enabled": true,
      "email_enabled": false,
      "default_reminder_minutes": 15
    },
    "ai": {
      "suggestions_enabled": true,
      "voice_input_enabled": true,
      "auto_categorize": true
    }
  }
}
```

### PUT /settings
Update user settings.

**Request:**
```json
{
  "preferences": {
    "language": "zh",
    "time_format": "24h"
  },
  "notifications": {
    "push_enabled": true,
    "default_reminder_minutes": 30
  }
}
```

### PUT /settings/profile
Update user profile.

**Request:**
```json
{
  "name": "John Smith",
  "avatar_file_id": "file_avatar_001"
}
```

### DELETE /settings/account
Delete user account.

**Request:**
```json
{
  "password": "current_password",
  "confirmation": "DELETE"
}
```

---

## Error Responses

All endpoints may return the following error format:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid date format",
    "details": {
      "field": "date",
      "expected": "YYYY-MM-DD",
      "received": "30-11-2025"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| UNAUTHORIZED | 401 | Missing or invalid authentication |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| VALIDATION_ERROR | 400 | Invalid request data |
| CONFLICT | 409 | Resource conflict (e.g., duplicate) |
| RATE_LIMITED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

---

## Webhooks (Optional)

### Event Webhooks

Configure webhooks to receive real-time updates:

**POST /webhooks**
```json
{
  "url": "https://your-server.com/webhook",
  "events": ["event.created", "event.updated", "event.deleted", "event.completed"]
}
```

**Webhook Payload:**
```json
{
  "event_type": "event.created",
  "timestamp": "2025-11-30T10:00:00Z",
  "data": {
    "id": "evt_001",
    "title": "New Event",
    "date": "2025-12-01"
  }
}
```

---

## Rate Limits

| Endpoint Type | Rate Limit |
|---------------|------------|
| Standard API | 100 requests/minute |
| AI Endpoints | 20 requests/minute |
| File Upload | 10 requests/minute |
| Agent API | 50 requests/minute |

---

## SDK/Client Integration

### JavaScript/TypeScript
```typescript
import { JarvisClient } from '@jarvis/sdk';

const client = new JarvisClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.jarvis-calendar.com/v1'
});

// Get events
const events = await client.events.list({ date: '2025-11-30' });

// Create event via AI
const parsed = await client.ai.parseEvent('Meeting tomorrow at 3pm');
const newEvent = await client.events.create(parsed.data.parsed);

// Agent integration
const agentClient = new JarvisAgentClient({
  agentId: 'agent_001',
  agentToken: 'agent-token'
});
const schedule = await agentClient.getSchedule('2025-11-30', '2025-12-07');
```

---

## Changelog

### v1.0.0 (2025-11-30)
- Initial API release
- Events CRUD operations
- Calendar types management
- AI natural language parsing
- Smart reminders
- User settings
- Agent integration endpoints
