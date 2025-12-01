# Jarvis Calendar - Complete Backend API Documentation

## Overview

This document provides comprehensive API specifications for the Jarvis Calendar backend, covering all frontend functionality requirements.

### Base Configuration
```
Base URL: https://api.jarvis-calendar.com/v1
Content-Type: application/json
Authorization: Bearer <access_token>
```

### Standard Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "server_time": "2025-12-01T10:30:00Z"
}
```

> **Important**: All responses include `server_time` which is the current server timestamp. Frontend should use this for "today" calculations to ensure consistency.

---

## 1. Authentication Module

### POST /auth/login
Login with account ID. Creates new account if not exists.

**Request:**
```json
{
  "account_id": "jarvis@cuhk.com"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400,
    "is_new_user": false,
    "user": {
      "account_id": "jarvis@cuhk.com",
      "home_address": "123 Main Street, Sha Tin",
      "school_address": "CUHK, Sha Tin, Hong Kong",
      "created_at": "2025-11-01T00:00:00Z"
    }
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

### POST /auth/logout
Logout and invalidate token.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully",
  "server_time": "2025-12-01T10:30:00Z"
}
```

---

## 2. User Module

### GET /user
Get current user information.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "account_id": "jarvis@cuhk.com",
    "home_address": "123 Main Street, Sha Tin",
    "school_address": "CUHK, Sha Tin, Hong Kong",
    "current_location": {
      "latitude": 22.4196,
      "longitude": 114.2068,
      "accuracy": 10,
      "timestamp": "2025-12-01T10:25:00Z"
    },
    "created_at": "2025-11-01T00:00:00Z",
    "updated_at": "2025-12-01T10:00:00Z"
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

### PUT /user
Update user information (addresses).

**Request:**
```json
{
  "home_address": "456 New Street, Sha Tin",
  "school_address": "CUHK, Sha Tin, Hong Kong"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "account_id": "jarvis@cuhk.com",
    "home_address": "456 New Street, Sha Tin",
    "school_address": "CUHK, Sha Tin, Hong Kong",
    "updated_at": "2025-12-01T10:30:00Z"
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

### POST /user/location
Update user's current location.

**Request:**
```json
{
  "latitude": 22.4196,
  "longitude": 114.2068,
  "accuracy": 10
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "location_id": "loc_001",
    "latitude": 22.4196,
    "longitude": 114.2068,
    "accuracy": 10,
    "timestamp": "2025-12-01T10:30:00Z"
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

### GET /user/location
Get user's last known location.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "latitude": 22.4196,
    "longitude": 114.2068,
    "accuracy": 10,
    "address": "Near CUHK MTR Station",
    "timestamp": "2025-12-01T10:25:00Z"
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

---

## 3. Server Time Module

### GET /time
Get current server time. **Critical for "Today" button functionality.**

**Response (200):**
```json
{
  "success": true,
  "data": {
    "server_time": "2025-12-01T10:30:00Z",
    "timezone": "UTC",
    "date": "2025-12-01",
    "timestamp": 1733051400000
  }
}
```

> **Frontend Usage**: When user clicks "Today" button, frontend should either:
> 1. Use `new Date()` for client time, OR
> 2. Call `GET /time` for server time to ensure sync across devices

---

## 4. Events Module

### GET /events
Get events with filters.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| date | string | No | Specific date (YYYY-MM-DD) |
| start_date | string | No | Range start (YYYY-MM-DD) |
| end_date | string | No | Range end (YYYY-MM-DD) |
| type_id | string | No | Filter by calendar type |
| completed | boolean | No | Filter by completion status |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "id": "evt_001",
        "title": "KAI BIRTHDAY TOMORROW",
        "date": "2025-12-01",
        "is_all_day": true,
        "start_time": null,
        "end_time": null,
        "location": null,
        "description": null,
        "type_id": "events",
        "color": "#F59E0B",
        "completed": false,
        "expanded": false,
        "links": [],
        "attachment": null,
        "created_at": "2025-11-25T08:00:00Z",
        "updated_at": "2025-11-25T08:00:00Z"
      },
      {
        "id": "evt_002",
        "title": "SIGN UP TO UNI",
        "date": "2025-12-01",
        "is_all_day": true,
        "start_time": null,
        "end_time": null,
        "location": null,
        "description": null,
        "type_id": "events",
        "color": "#F59E0B",
        "completed": true,
        "expanded": false,
        "links": ["https://university.edu/apply"],
        "attachment": {
          "id": "file_001",
          "name": "DOcs.pdf",
          "url": "https://storage.example.com/files/DOcs.pdf",
          "size": 102400,
          "mime_type": "application/pdf"
        },
        "created_at": "2025-11-25T09:00:00Z",
        "updated_at": "2025-12-01T08:00:00Z"
      },
      {
        "id": "evt_003",
        "title": "Therapy",
        "date": "2025-12-01",
        "is_all_day": false,
        "start_time": "15:00",
        "end_time": "17:00",
        "location": "Clinic",
        "description": null,
        "type_id": "routine",
        "color": "#EC4899",
        "completed": false,
        "expanded": false,
        "links": [],
        "attachment": null,
        "created_at": "2025-11-20T10:00:00Z",
        "updated_at": "2025-11-20T10:00:00Z"
      }
    ],
    "total": 3
  },
  "server_time": "2025-12-01T10:30:00Z"
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
    "title": "KAI BIRTHDAY TOMORROW",
    "date": "2025-12-01",
    "is_all_day": true,
    "start_time": null,
    "end_time": null,
    "location": null,
    "description": "Don't forget the gift!",
    "type_id": "events",
    "color": "#F59E0B",
    "completed": false,
    "links": [],
    "attachment": null,
    "created_at": "2025-11-25T08:00:00Z",
    "updated_at": "2025-11-25T08:00:00Z"
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

### POST /events
Create new event.

**Request:**
```json
{
  "title": "Doctor Appointment",
  "date": "2025-12-02",
  "is_all_day": false,
  "start_time": "14:00",
  "end_time": "15:00",
  "location": "City Hospital",
  "description": "Annual checkup",
  "type_id": "routine",
  "links": [],
  "attachment_id": null
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "evt_new_001",
    "title": "Doctor Appointment",
    "date": "2025-12-02",
    "is_all_day": false,
    "start_time": "14:00",
    "end_time": "15:00",
    "location": "City Hospital",
    "description": "Annual checkup",
    "type_id": "routine",
    "color": "#EC4899",
    "completed": false,
    "created_at": "2025-12-01T10:30:00Z"
  },
  "message": "Event created successfully",
  "server_time": "2025-12-01T10:30:00Z"
}
```

### PUT /events/:id
Update event.

**Request:**
```json
{
  "title": "Doctor Appointment - Updated",
  "start_time": "15:00",
  "end_time": "16:00",
  "location": "New Hospital Location"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "evt_new_001",
    "title": "Doctor Appointment - Updated",
    "start_time": "15:00",
    "end_time": "16:00",
    "location": "New Hospital Location",
    "updated_at": "2025-12-01T11:00:00Z"
  },
  "message": "Event updated successfully",
  "server_time": "2025-12-01T11:00:00Z"
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
    "id": "evt_001",
    "completed": true,
    "completed_at": "2025-12-01T10:30:00Z"
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

### DELETE /events/:id
Delete event.

**Response (200):**
```json
{
  "success": true,
  "message": "Event deleted successfully",
  "server_time": "2025-12-01T10:30:00Z"
}
```

### POST /events/:id/links
Add link to event.

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
      "https://university.edu/apply",
      "https://docs.google.com/document/d/123"
    ]
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

### DELETE /events/:id/links
Remove link from event.

**Request:**
```json
{
  "url": "https://docs.google.com/document/d/123"
}
```

### POST /events/:id/share
Generate shareable screenshot of event.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "screenshot_url": "https://storage.example.com/screenshots/evt_001.png",
    "expires_at": "2025-12-02T10:30:00Z"
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

---

## 5. Calendar Types Module

### GET /calendar-types
Get all calendar types.

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "general",
      "name": "General",
      "color": "#6B7280",
      "is_visible": true,
      "is_deletable": false,
      "event_count": 15
    },
    {
      "id": "routine",
      "name": "Routine",
      "color": "#EC4899",
      "is_visible": true,
      "is_deletable": true,
      "event_count": 8
    },
    {
      "id": "events",
      "name": "Events",
      "color": "#F59E0B",
      "is_visible": true,
      "is_deletable": true,
      "event_count": 12
    },
    {
      "id": "holidays",
      "name": "Holidays",
      "color": "#3B82F6",
      "is_visible": true,
      "is_deletable": true,
      "event_count": 5
    },
    {
      "id": "school",
      "name": "School",
      "color": "#22C55E",
      "is_visible": true,
      "is_deletable": true,
      "event_count": 20
    }
  ],
  "server_time": "2025-12-01T10:30:00Z"
}
```

### POST /calendar-types
Create new calendar type.

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
    "id": "fitness_001",
    "name": "Fitness",
    "color": "#10B981",
    "is_visible": true,
    "is_deletable": true,
    "event_count": 0
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

### PUT /calendar-types/:id
Update calendar type.

**Request:**
```json
{
  "name": "Workout",
  "color": "#059669"
}
```

### PATCH /calendar-types/:id/visibility
Toggle type visibility.

**Request:**
```json
{
  "is_visible": false
}
```

### DELETE /calendar-types/:id
Delete calendar type. All events of this type will be moved to "General".

**Response (200):**
```json
{
  "success": true,
  "data": {
    "events_moved": 5
  },
  "message": "Calendar type deleted. 5 events moved to General.",
  "server_time": "2025-12-01T10:30:00Z"
}
```

---

## 6. Smart Reminders Module

### GET /reminders
Get smart reminders for carousel display.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| date | string | Date for reminders (default: today from server_time) |

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
      }
    },
    {
      "id": "rem_commute",
      "type": "commute",
      "title": "通勤信息",
      "subtitle": "前往学校约需 25 分钟，距离 8.5 公里",
      "bg_color": "#E8F5E9",
      "icon_bg": "#4ADE80",
      "data": {
        "from": "home",
        "to": "school",
        "duration_minutes": 25,
        "distance_km": 8.5,
        "traffic_status": "normal"
      },
      "action_url": "https://maps.google.com/..."
    },
    {
      "id": "rem_birthday",
      "type": "important",
      "title": "重要提醒",
      "subtitle": "明天是 Kai 的生日，记得准备礼物 🎁",
      "bg_color": "#FCE4EC",
      "icon_bg": "#F472B6",
      "data": {
        "related_event_id": "evt_106",
        "person_name": "Kai",
        "event_date": "2025-12-02"
      }
    }
  ],
  "server_time": "2025-12-01T10:30:00Z"
}
```

### GET /location/commute
Get detailed commute information.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| from | string | "home", "school", "current", or coordinates "lat,lng" |
| to | string | "home", "school", or coordinates "lat,lng" |

**Response (200):**
```json
{
  "success": true,
  "data": {
    "from": {
      "type": "home",
      "address": "123 Main Street, Sha Tin",
      "coordinates": { "lat": 22.3964, "lng": 114.1095 }
    },
    "to": {
      "type": "school",
      "address": "CUHK, Sha Tin, Hong Kong",
      "coordinates": { "lat": 22.4196, "lng": 114.2068 }
    },
    "routes": [
      {
        "mode": "driving",
        "duration_minutes": 25,
        "distance_km": 8.5,
        "traffic_status": "normal"
      },
      {
        "mode": "transit",
        "duration_minutes": 35,
        "distance_km": 9.2,
        "transit_details": "MTR East Rail Line"
      }
    ],
    "maps_url": "https://maps.google.com/?saddr=22.3964,114.1095&daddr=22.4196,114.2068"
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

---

## 7. File Upload Module

### POST /files/upload
Upload file attachment.

**Request (multipart/form-data):**
```
file: <binary>
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
    "created_at": "2025-12-01T10:30:00Z"
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

### DELETE /files/:id
Delete uploaded file.

**Response (200):**
```json
{
  "success": true,
  "message": "File deleted successfully",
  "server_time": "2025-12-01T10:30:00Z"
}
```

---

## 8. AI Integration Module

### POST /ai/quick-add
Quick add task via natural language (for "Add a Task for Today" button).

**Request:**
```json
{
  "text": "买牛奶回家的路上",
  "context": {
    "current_date": "2025-12-01",
    "timezone": "Asia/Hong_Kong"
  }
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "event": {
      "id": "evt_ai_001",
      "title": "买牛奶",
      "date": "2025-12-01",
      "is_all_day": true,
      "type_id": "general",
      "color": "#6B7280",
      "completed": false
    },
    "parsed_intent": "task_creation",
    "confidence": 0.95
  },
  "message": "已添加任务：买牛奶",
  "server_time": "2025-12-01T10:30:00Z"
}
```

### POST /ai/parse-event
Parse natural language to event data (for Create Event modal AI input).

**Request:**
```json
{
  "text": "明天下午3点在星巴克和John开会，大概1小时",
  "context": {
    "current_date": "2025-12-01",
    "timezone": "Asia/Hong_Kong"
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "parsed": {
      "title": "和John开会",
      "date": "2025-12-02",
      "is_all_day": false,
      "start_time": "15:00",
      "end_time": "16:00",
      "location": "星巴克",
      "suggested_type_id": "events"
    },
    "confidence": 0.92,
    "raw_entities": {
      "time": "明天下午3点",
      "duration": "1小时",
      "location": "星巴克",
      "person": "John"
    }
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

### POST /ai/parse-calendar-type
Parse natural language to create calendar type (for Create Type modal AI input).

**Request:**
```json
{
  "text": "创建一个绿色的健身分类"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "parsed": {
      "name": "健身",
      "color": "#22C55E"
    },
    "confidence": 0.90
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

---

## 9. AI Agent Module (External Agent Access)

These endpoints are designed for external AI agents to interact with user's calendar.

### GET /ai/agent/user-data
Agent retrieves user's complete data including location and addresses.

**Headers:**
```
Authorization: Bearer <agent_access_token>
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
    "user": {
      "account_id": "jarvis@cuhk.com",
      "home_address": "123 Main Street, Sha Tin",
      "school_address": "CUHK, Sha Tin, Hong Kong",
      "current_location": {
        "latitude": 22.4196,
        "longitude": 114.2068,
        "accuracy": 10,
        "timestamp": "2025-12-01T10:25:00Z"
      }
    },
    "events": [
      {
        "id": "evt_001",
        "title": "Team Meeting",
        "date": "2025-12-01",
        "start_time": "10:00",
        "end_time": "11:00",
        "location": "Conference Room",
        "type_name": "Events",
        "completed": false
      }
    ],
    "calendar_types": [
      { "id": "general", "name": "General", "color": "#6B7280" },
      { "id": "routine", "name": "Routine", "color": "#EC4899" },
      { "id": "events", "name": "Events", "color": "#F59E0B" },
      { "id": "holidays", "name": "Holidays", "color": "#3B82F6" },
      { "id": "school", "name": "School", "color": "#22C55E" }
    ],
    "summary": {
      "total_events": 15,
      "completed": 5,
      "pending": 10,
      "today": 4,
      "tomorrow": 2,
      "this_week": 12
    }
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

### POST /ai/agent/action
Agent performs action on user's calendar.

**Request:**
```json
{
  "agent_id": "agent_jarvis_001",
  "action": "create_event",
  "payload": {
    "title": "Reminder: Call Mom",
    "date": "2025-12-02",
    "is_all_day": true,
    "type_id": "general"
  },
  "reason": "User requested via voice command"
}
```

**Available Actions:**
- `create_event` - Create new event
- `update_event` - Update existing event
- `delete_event` - Delete event
- `complete_event` - Mark event as complete

**Response (200):**
```json
{
  "success": true,
  "data": {
    "action_id": "action_001",
    "action": "create_event",
    "result": {
      "event_id": "evt_agent_001",
      "status": "created"
    }
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

### POST /ai/agent/suggest
Get AI-powered suggestions for the user.

**Request:**
```json
{
  "context": {
    "current_date": "2025-12-01",
    "current_time": "10:30",
    "user_location": { "lat": 22.4196, "lng": 114.2068 }
  },
  "request_type": "daily_briefing"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "briefing": "今天有4个日程安排。天气不错，适合外出。别忘了明天是Kai的生日！",
    "suggestions": [
      {
        "type": "reminder",
        "message": "明天是Kai的生日，要不要现在设置一个买礼物的提醒？",
        "action": {
          "type": "create_event",
          "payload": {
            "title": "买生日礼物",
            "date": "2025-12-01",
            "is_all_day": true
          }
        }
      },
      {
        "type": "commute",
        "message": "您15:00有Therapy预约，建议14:35出发",
        "data": {
          "event_id": "evt_003",
          "suggested_departure": "14:35"
        }
      }
    ]
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

---

## 10. Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": { ... }
  },
  "server_time": "2025-12-01T10:30:00Z"
}
```

### Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| UNAUTHORIZED | 401 | Missing or invalid authentication |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| VALIDATION_ERROR | 400 | Invalid request data |
| DUPLICATE_ACCOUNT | 409 | Account ID already exists |
| TYPE_NOT_DELETABLE | 400 | Cannot delete default type |
| FILE_TOO_LARGE | 413 | File exceeds size limit (10MB) |
| RATE_LIMITED | 429 | Too many requests |
| AI_PARSE_FAILED | 422 | AI could not parse input |
| LOCATION_ERROR | 400 | Invalid location data |
| INTERNAL_ERROR | 500 | Server internal error |

---

## 11. Frontend Feature → API Mapping

### Authentication
| Frontend Feature | API Endpoint |
|------------------|--------------|
| Login | POST /auth/login |
| Logout | POST /auth/logout |

### User Settings
| Frontend Feature | API Endpoint |
|------------------|--------------|
| Get account info | GET /user |
| Update addresses | PUT /user |
| Get current location | GET /user/location |
| Update location | POST /user/location |

### Calendar Navigation
| Frontend Feature | API Endpoint |
|------------------|--------------|
| Get today's date | GET /time |
| View events by date | GET /events?date=YYYY-MM-DD |
| Today button | GET /time + GET /events?date=<today> |

### Event Management
| Frontend Feature | API Endpoint |
|------------------|--------------|
| List events | GET /events |
| Create event | POST /events |
| Edit event | PUT /events/:id |
| Delete event | DELETE /events/:id |
| Toggle complete | PATCH /events/:id/complete |
| Add link | POST /events/:id/links |
| Remove link | DELETE /events/:id/links |
| Upload attachment | POST /files/upload |
| Share (screenshot) | POST /events/:id/share |

### Calendar Types
| Frontend Feature | API Endpoint |
|------------------|--------------|
| List types | GET /calendar-types |
| Create type | POST /calendar-types |
| Update type | PUT /calendar-types/:id |
| Toggle visibility | PATCH /calendar-types/:id/visibility |
| Delete type | DELETE /calendar-types/:id |

### Smart Reminders
| Frontend Feature | API Endpoint |
|------------------|--------------|
| Get reminders carousel | GET /reminders |
| Get commute info | GET /location/commute |

### AI Features
| Frontend Feature | API Endpoint |
|------------------|--------------|
| Quick add task (button) | POST /ai/quick-add |
| Event AI input | POST /ai/parse-event |
| Type AI input | POST /ai/parse-calendar-type |

### Agent Integration (已实现)
| Feature | API Endpoint |
|---------|--------------|
| Read user/schedule info | GET /agent/info |
| Perform action | POST /agent/action |

---

## 12. Agent API Details

### GET /agent/info
获取完整的用户信息和日程数据，供AI Agent使用。

**Query Parameters:**
- `start_date` (optional): 日期范围起始 (YYYY-MM-DD)，默认今天
- `end_date` (optional): 日期范围结束 (YYYY-MM-DD)，默认30天后

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "account_id": "jarvis@cuhk.com",
      "home_address": "123 Main Street, Sha Tin",
      "school_address": "CUHK, Sha Tin, Hong Kong"
    },
    "location": {
      "current": {
        "latitude": 22.4199,
        "longitude": 114.2073,
        "accuracy": 15,
        "timestamp": "2025-12-01T08:00:00Z"
      },
      "previous": {
        "latitude": 22.3964,
        "longitude": 114.1095,
        "accuracy": 20,
        "timestamp": "2025-11-30T18:00:00Z"
      }
    },
    "calendar_types": [...],
    "events": [...],
    "summary": {
      "total_events": 15,
      "completed_events": 5,
      "pending_events": 10,
      "today_events": 4
    }
  }
}
```

### POST /agent/action
Agent 代理执行操作。

**Supported Actions:**
| Action | Payload Fields |
|--------|----------------|
| `create_event` | title, date, is_all_day, start_time, end_time, location, description, type_id, links |
| `update_event` | event_id, (任意event字段) |
| `delete_event` | event_id |
| `complete_event` | event_id, completed (boolean) |
| `create_calendar_type` | name, color |

---

## 13. Rate Limits

| Endpoint Type | Limit |
|---------------|-------|
| Standard API | 100 req/min |
| AI Endpoints | 20 req/min |
| File Upload | 10 req/min |
| Agent API | 50 req/min |

---

## Changelog

### v1.0.0 (2025-12-01)
- Initial API version
- Authentication with account ID
- User profile with addresses and location
- Real-time server time for "today" sync
- Events CRUD with attachments and links
- Calendar types management
- Smart reminders (weather, commute, important)
- AI natural language parsing
- External agent integration endpoints
