# Jarvis Calendar - AI Agent 集成文档

本文档详细说明了如何将外部 AI Agent 集成到 Jarvis Calendar 应用程序中。

---

## 📋 目录

1. [系统架构概述](#系统架构概述)
2. [API 端点说明](#api-端点说明)
3. [功能 A: Add a Task for Today](#功能-a-add-a-task-for-today)
4. [功能 B: Create Calendar Type](#功能-b-create-calendar-type)
5. [功能 C: Create Event](#功能-c-create-event)
6. [功能 D: AI Reminder](#功能-d-ai-reminder)
7. [Agent 配置指南](#agent-配置指南)
8. [错误处理](#错误处理)
9. [测试指南](#测试指南)

---

## 系统架构概述

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Vue Frontend  │ ──► │  Django Backend │ ◄── │   AI Agent      │
│   (用户界面)     │     │  (API 服务)      │     │  (外部服务)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         │  1. 用户输入           │                       │
         │ ──────────────────►  │                       │
         │                       │  2. 转发请求到 Agent   │
         │                       │ ──────────────────►  │
         │                       │                       │
         │                       │  3. Agent 返回结果     │
         │                       │ ◄──────────────────  │
         │  4. 返回处理结果        │                       │
         │ ◄──────────────────  │                       │
```

### 数据流说明

1. **前端** → **后端**: 用户输入自然语言文本
2. **后端** → **Agent**: 后端收集上下文数据，转发给 AI Agent
3. **Agent** → **后端**: Agent 解析后返回结构化数据
4. **后端** → **前端**: 后端处理数据并返回给前端

---

## API 端点说明

### 基础 URL
```
http://localhost:8000/api/v1
```

### 认证方式
所有 Agent API 需要 Bearer Token 认证：
```
Authorization: Bearer <access_token>
```

### Agent 相关端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/agent/reminder-context` | GET | 获取 AI Reminder 上下文数据 |
| `/agent/parse-task` | POST | 解析并创建今日任务（自动返回available_types） |
| `/agent/parse-calendar-type` | POST | 解析日历类型（自动返回available_colors） |
| `/agent/parse-event` | POST | 解析事件信息（自动返回available_types） |
| `/agent/generate-reminders` | POST | 生成智能提醒 |

> ⚠️ **重要**: 所有 parse 接口都采用**两阶段模式**：
> 1. **第一阶段**: 发送 `user_input` → 后端返回上下文（available_types/available_colors）
> 2. **第二阶段**: Agent解析后发送结构化数据 → 后端处理并返回结果

---

## 功能 A: Add a Task for Today

### 功能描述
用户在 AITaskDialog 输入自然语言，Agent 解析后**直接创建**一个事件到今天。

### 流程（两阶段POST）
```
1. 前端发送 user_input → 后端返回上下文（包含 available_types）
2. Agent 使用上下文解析用户输入
3. Agent 发送解析后的结构化数据 → 后端创建事件并返回结果
```

### API: `/agent/parse-task`

#### 阶段1: 发送用户输入，获取上下文

```http
POST /api/v1/agent/parse-task
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_input": "下午三点开会讨论项目进度"
}
```

**响应（包含上下文，供Agent使用）：**
```json
{
  "success": true,
  "data": {
    "user_input": "下午三点开会讨论项目进度",
    "available_types": [
      {"id": "general", "name": "General", "color": "#6B7280"},
      {"id": "routine", "name": "Routine", "color": "#EC4899"},
      {"id": "events", "name": "Events", "color": "#F59E0B"},
      {"id": "school", "name": "School", "color": "#22C55E"}
    ],
    "default_type_id": "general",
    "date": "2025-12-02",
    "message": "Agent请从available_types中选择type_id..."
  },
  "server_time": "2025-12-02T10:00:00Z"
}
```

#### 阶段2: Agent 提交解析结果

> ⚠️ **重要**: Agent 必须从阶段1返回的 `available_types` 中选择 `type_id`

```http
POST /api/v1/agent/parse-task
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "开会讨论项目进度",
  "type_id": "general",
  "is_all_day": false,
  "start_time": "15:00",
  "end_time": "16:00",
  "location": ""
}
```

**响应（事件创建成功）：**
```json
{
  "success": true,
  "data": {
    "event": { ... },
    "available_types": [...],
    "message": "Task '开会讨论项目进度' created for today"
  }
}
```

#### Agent 需要返回的数据格式

> ⚠️ **重要**: 
> - 日期固定为今天，Agent **无需返回 date 字段**
> - `type_id` **必须是 available_types 中存在的 id**

```json
{
  "title": "开会讨论项目进度",
  "type_id": "general",
  "is_all_day": false,
  "start_time": "15:00",
  "end_time": "16:00",
  "location": ""
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | ✅ 是 | 任务标题 |
| `type_id` | string | 否 | 日历类型ID，**必须是 available_types 中的 id**，默认 "general" |
| `is_all_day` | boolean | 否 | 是否全天事件，默认 true |
| `start_time` | string | 否 | 开始时间，格式 "HH:MM"（仅当 is_all_day=false 时有效） |
| `end_time` | string | 否 | 结束时间，格式 "HH:MM"（仅当 is_all_day=false 时有效） |
| `location` | string | 否 | 地点 |

#### 前端表单字段参考
前端 CreateEventModal 表单包含以下字段：
- Title（标题）
- Date（日期）- **此功能锁定为今天**
- All day（全天开关）
- Start Time / End Time（时间）
- Location（地点）
- Calendar Type（日历类型）
- Links（链接）- 用户手动添加
- Attachment（附件）- 用户手动上传

#### 响应

> ⚠️ 响应包含完整的事件字段，与前端 `transformEventFromBackend` 对齐

```json
{
  "success": true,
  "data": {
    "event": {
      "id": "uuid",
      "title": "开会讨论项目进度",
      "date": "2025-12-02",
      "is_all_day": false,
      "start_time": "15:00",
      "end_time": "16:00",
      "location": "",
      "type_id": "general",
      "color": "#6B7280",
      "completed": false,
      "expanded": false,
      "links": [],
      "attachment": null
    },
    "message": "Task '开会讨论项目进度' created for today"
  },
  "server_time": "2025-12-02T10:00:00Z"
}
```

#### 完整字段说明（后端响应）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 事件唯一ID |
| `title` | string | 事件标题 |
| `date` | string | 日期，格式 "YYYY-MM-DD" |
| `is_all_day` | boolean | 是否全天事件 |
| `start_time` | string/null | 开始时间，格式 "HH:MM" |
| `end_time` | string/null | 结束时间，格式 "HH:MM" |
| `location` | string | 地点 |
| `type_id` | string | 日历类型ID |
| `color` | string | 日历类型颜色 |
| `completed` | boolean | 是否已完成 |
| `expanded` | boolean | UI展开状态 |
| `links` | array | 链接数组，如 `["http://..."]` |
| `attachment` | object/null | 附件对象或null |

### Agent 实现示例 (Python)

```python
import requests

def parse_task(user_input: str, access_token: str, api_base: str) -> dict:
    """
    解析用户输入的任务描述，返回结构化数据
    
    示例输入：
    - "下午三点开会"
    - "明天提交报告" (注意：日期会被忽略，强制为今天)
    - "买牛奶"
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 阶段1: 发送 user_input，获取上下文（available_types）
    context_resp = requests.post(
        f"{api_base}/agent/parse-task",
        headers=headers,
        json={"user_input": user_input}  # 只发送 user_input
    )
    context = context_resp.json()["data"]
    available_types = context["available_types"]
    
    # 构建可用类型列表供LLM参考
    type_options = ", ".join([f'{t["id"]}({t["name"]})' for t in available_types])
    
    # 阶段2: 使用 LLM 解析用户输入
    prompt = f"""
    解析以下任务描述，提取结构化信息：
    
    输入：{user_input}
    
    注意：
    1. 日期固定为今天，无需返回date字段
    2. type_id 必须从以下选项中选择: {type_options}
    
    请返回 JSON 格式：
    {{
        "title": "任务标题",
        "is_all_day": true/false,
        "start_time": "HH:MM 或 null",
        "end_time": "HH:MM 或 null",
        "location": "地点或空字符串",
        "type_id": "从可用选项中选择"
    }}
    """
    
    result = call_llm(prompt)
    
    # 验证 type_id 是否有效
    valid_type_ids = [t["id"] for t in available_types]
    if result.get("type_id") not in valid_type_ids:
        result["type_id"] = "general"  # 默认类型
    
    # 阶段3: 提交解析结果到后端（同一个endpoint，不同参数）
    create_resp = requests.post(
        f"{api_base}/agent/parse-task",
        headers=headers,
        json=result  # 发送 title, type_id 等解析后的字段
    )
    return create_resp.json()
```

---

## 功能 B: Create Calendar Type

### 功能描述
用户在 CreateCalendarTypeModal 输入描述，Agent 解析后**自动填入表单**，用户确认后再创建。

### 流程（两阶段POST）
```
1. 前端发送 user_input → 后端返回上下文（包含 available_colors）
2. Agent 使用上下文解析用户输入
3. Agent 发送解析后的结构化数据 → 后端验证并返回结果
4. 前端填入表单 → 用户确认 → 创建
```

### API: `/agent/parse-calendar-type`

#### 阶段1: 发送用户输入，获取上下文

```http
POST /api/v1/agent/parse-calendar-type
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_input": "创建一个粉色的健身类型"
}
```

**响应（包含上下文，供Agent使用）：**
```json
{
  "success": true,
  "data": {
    "user_input": "创建一个粉色的健身类型",
    "available_colors": [
      {"name": "Amber", "value": "#F59E0B"},
      {"name": "Pink", "value": "#EC4899"},
      {"name": "Blue", "value": "#3B82F6"},
      {"name": "Green", "value": "#22C55E"},
      {"name": "Purple", "value": "#A855F7"},
      {"name": "Red", "value": "#EF4444"}
    ],
    "message": "Agent请从available_colors中选择一个颜色的value..."
  },
  "server_time": "2025-12-02T10:00:00Z"
}
```

#### 阶段2: Agent 提交解析结果

> ⚠️ **重要**: Agent 必须从阶段1返回的 `available_colors` 中选择 `color`（使用 value 字段）

```http
POST /api/v1/agent/parse-calendar-type
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "健身",
  "color": "#EC4899"
}
```

**响应（验证成功）：**
```json
{
  "success": true,
  "data": {
    "parsed": {
      "name": "健身",
      "color": "#EC4899"
    },
    "available_colors": [...],
    "message": "Calendar type parsed successfully"
  },
  "server_time": "2025-12-02T10:00:00Z"
}
```

#### Agent 需要返回的数据格式
```json
{
  "name": "健身",
  "color": "#EC4899"
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ 是 | 类型名称 |
| `color` | string | ✅ 是 | 颜色代码（**必须是 available_colors 中的 value 之一**） |

#### ⚠️ 固定颜色列表（必须精确匹配）

**重要：前端只支持以下6种颜色，color字段必须是其中之一，不区分大小写：**

| 颜色名 | 颜色代码 | 说明 |
|--------|----------|------|
| Amber | `#F59E0B` | 琥珀/黄色 |
| Pink | `#EC4899` | 粉色 |
| Blue | `#3B82F6` | 蓝色 |
| Green | `#22C55E` | 绿色 |
| Purple | `#A855F7` | 紫色 |
| Red | `#EF4444` | 红色 |

**如果传入的颜色不在列表中，API会返回错误！**

#### 错误响应示例（颜色无效）
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid color '#FFFFFF'. Must be one of: #F59E0B, #EC4899, #3B82F6, #22C55E, #A855F7, #EF4444"
  },
  "server_time": "2025-12-02T10:00:00Z"
}
```

### Agent 实现示例 (Python)

```python
# 前端固定的6种可用颜色（必须使用其中之一）
VALID_COLORS = ['#F59E0B', '#EC4899', '#3B82F6', '#22C55E', '#A855F7', '#EF4444']

def parse_calendar_type(user_input: str) -> dict:
    """
    解析日历类型描述
    
    示例输入：
    - "创建一个粉色的健身类型"
    - "工作相关的蓝色日历"
    - "新建学习类型"
    
    ⚠️ 重要：color 字段是必填的，且必须是 VALID_COLORS 中的一个值！
    """
    
    # 颜色关键词映射到固定颜色
    color_map = {
        # 中文
        "粉色": "#EC4899", "粉": "#EC4899", "粉红": "#EC4899",
        "蓝色": "#3B82F6", "蓝": "#3B82F6",
        "绿色": "#22C55E", "绿": "#22C55E",
        "紫色": "#A855F7", "紫": "#A855F7",
        "红色": "#EF4444", "红": "#EF4444",
        "黄色": "#F59E0B", "黄": "#F59E0B", "琥珀": "#F59E0B", "橙": "#F59E0B",
        # 英文
        "pink": "#EC4899",
        "blue": "#3B82F6",
        "green": "#22C55E",
        "purple": "#A855F7",
        "red": "#EF4444",
        "amber": "#F59E0B", "yellow": "#F59E0B", "orange": "#F59E0B",
    }
    
    prompt = f"""
    解析以下日历类型描述：
    
    输入：{user_input}
    
    请返回 JSON 格式：
    {{
        "name": "类型名称",
        "color_hint": "用户提到的颜色关键词或 null"
    }}
    """
    
    result = call_llm(prompt)
    
    # 匹配颜色 - 必须是有效颜色之一
    color = None
    if result.get("color_hint"):
        hint = result["color_hint"].lower()
        color = color_map.get(hint)
    
    # 如果没有匹配到颜色，根据类型名称智能选择一个默认颜色
    if not color:
        # 根据类型名称关键词选择合适的颜色
        name_lower = result["name"].lower()
        if any(k in name_lower for k in ["work", "工作", "会议", "meeting"]):
            color = "#3B82F6"  # Blue
        elif any(k in name_lower for k in ["fitness", "健身", "运动", "sport", "gym"]):
            color = "#EC4899"  # Pink
        elif any(k in name_lower for k in ["study", "学习", "school", "学校"]):
            color = "#22C55E"  # Green
        elif any(k in name_lower for k in ["event", "活动", "party", "聚会"]):
            color = "#F59E0B"  # Amber
        else:
            color = "#A855F7"  # Purple 作为通用默认
    
    return {
        "name": result["name"],
        "color": color  # 必须是 VALID_COLORS 中的值
    }
```

---

## 功能 C: Create Event

### 功能描述
用户在 CreateEventModal 输入描述，Agent 解析后**自动填入表单**，用户确认后再创建。

### 流程（两阶段POST）
```
1. 前端发送 user_input → 后端返回上下文（包含 available_types）
2. Agent 使用上下文解析用户输入
3. Agent 发送解析后的结构化数据 → 后端验证并返回结果
4. 前端填入表单 → 用户确认 → 创建事件
```

### API: `/agent/parse-event`

#### 阶段1: 发送用户输入，获取上下文

```http
POST /api/v1/agent/parse-event
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_input": "下周一下午2点到4点在图书馆学习"
}
```

**响应（包含上下文，供Agent使用）：**
```json
{
  "success": true,
  "data": {
    "user_input": "下周一下午2点到4点在图书馆学习",
    "available_types": [
      {"id": "general", "name": "General", "color": "#6B7280"},
      {"id": "routine", "name": "Routine", "color": "#EC4899"},
      {"id": "events", "name": "Events", "color": "#F59E0B"},
      {"id": "school", "name": "School", "color": "#22C55E"}
    ],
    "default_type_id": "general",
    "current_date": "2025-12-02",
    "message": "Agent请从available_types中选择type_id..."
  },
  "server_time": "2025-12-02T10:00:00Z"
}
```

#### 阶段2: Agent 提交解析结果

> ⚠️ **重要**: Agent 必须从阶段1返回的 `available_types` 中选择 `type_id`

```http
POST /api/v1/agent/parse-event
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "在图书馆学习",
  "date": "2025-12-09",
  "is_all_day": false,
  "start_time": "14:00",
  "end_time": "16:00",
  "location": "图书馆",
  "type_id": "school"
}
```

**响应（验证成功）：**
```json
{
  "success": true,
  "data": {
    "parsed": { ... },
    "available_types": [...],
    "message": "Event parsed successfully"
  },
  "server_time": "2025-12-02T10:00:00Z"
}
```

#### Agent 需要返回的数据格式

> ⚠️ **重要**: `type_id` **必须是 available_types 中存在的 id**

```json
{
  "title": "在图书馆学习",
  "date": "2025-12-09",
  "is_all_day": false,
  "start_time": "14:00",
  "end_time": "16:00",
  "location": "图书馆",
  "type_id": "school"
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | ✅ 是 | 事件标题 |
| `date` | string | 否 | 日期，格式 "YYYY-MM-DD"，默认今天 |
| `is_all_day` | boolean | 否 | 是否全天事件，默认 true |
| `start_time` | string | 否 | 开始时间，格式 "HH:MM"（仅当 is_all_day=false 时有效） |
| `end_time` | string | 否 | 结束时间，格式 "HH:MM"（仅当 is_all_day=false 时有效） |
| `location` | string | 否 | 地点 |
| `type_id` | string | 否 | 日历类型ID，**必须是 available_types 中的 id** |

#### 前端表单字段参考
前端 CreateEventModal 表单包含以下字段：
- Title（标题）
- Date（日期）
- All day（全天开关）
- Start Time / End Time（时间）
- Location（地点）
- Calendar Type（日历类型）
- Links（链接）- 用户手动添加
- Attachment（附件）- 用户手动上传

#### 响应
```json
{
  "success": true,
  "data": {
    "parsed": {
      "title": "在图书馆学习",
      "date": "2025-12-09",
      "is_all_day": false,
      "start_time": "14:00",
      "end_time": "16:00",
      "location": "图书馆",
      "type_id": "school"
    },
    "available_types": [
      {"id": "general", "name": "General", "color": "#6B7280"},
      {"id": "routine", "name": "Routine", "color": "#EC4899"},
      {"id": "events", "name": "Events", "color": "#F59E0B"},
      {"id": "school", "name": "School", "color": "#22C55E"}
    ],
    "message": "Event parsed successfully"
  },
  "server_time": "2025-12-02T10:00:00Z"
}
```

### Agent 实现示例 (Python)

```python
import requests
from datetime import datetime, timedelta

def parse_event(user_input: str, access_token: str, api_base: str) -> dict:
    """
    解析事件描述
    
    示例输入：
    - "下周一下午2点到4点在图书馆学习"
    - "明天早上9点面试"
    - "周五晚上和朋友聚餐"
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 阶段1: 发送 user_input，获取上下文（available_types）
    context_resp = requests.post(
        f"{api_base}/agent/parse-event",
        headers=headers,
        json={"user_input": user_input}  # 只发送 user_input
    )
    context = context_resp.json()["data"]
    available_types = context["available_types"]
    current_date = context["current_date"]
    
    # 构建可用类型列表供LLM参考
    type_options = ", ".join([f'{t["id"]}({t["name"]})' for t in available_types])
    valid_type_ids = [t["id"] for t in available_types]
    
    # 阶段2: 使用 LLM 解析用户输入
    prompt = f"""
    解析以下事件描述，当前日期是 {current_date}：
    
    输入：{user_input}
    
    注意：type_id 必须从以下选项中选择: {type_options}
    
    请返回 JSON 格式：
    {{
        "title": "事件标题",
        "date": "YYYY-MM-DD",
        "is_all_day": true/false,
        "start_time": "HH:MM 或 null",
        "end_time": "HH:MM 或 null",
        "location": "地点或空字符串",
        "type_id": "从可用选项中选择"
    }}
    """
    
    result = call_llm(prompt)
    
    # 验证 type_id 是否有效
    if result.get("type_id") not in valid_type_ids:
        result["type_id"] = "general"  # 默认类型
    
    # 阶段3: 提交解析结果到后端（同一个endpoint，不同参数）
    parse_resp = requests.post(
        f"{api_base}/agent/parse-event",
        headers=headers,
        json=result  # 发送 title, date, type_id 等解析后的字段
    )
    return parse_resp.json()
```

---

## 功能 D: AI Reminder

### 功能描述
AI Reminder 显示三个提醒卡片（天气、通勤、重要提醒），用户点击刷新按钮后，系统会：
1. 获取上下文数据（位置、地址、未来10天行程）
2. 发送给 Agent 处理
3. Agent 返回三个提醒卡片内容

### 流程
```
用户点击刷新 → 获取上下文 → 发送给 Agent → Agent 返回3个提醒 → 更新显示
```

### 步骤 1: 获取上下文数据

#### API: `/agent/reminder-context`

```http
GET /api/v1/agent/reminder-context
Authorization: Bearer <token>
```

#### 响应
```json
{
  "success": true,
  "data": {
    "user": {
      "account_id": "jarvis@cuhk.com",
      "home_address": "香港沙田大围",
      "school_address": "香港中文大学"
    },
    "current_location": {
      "latitude": 22.4196,
      "longitude": 114.2068,
      "accuracy": 10.5,
      "timestamp": "2025-12-02T10:00:00Z"
    },
    "events": [
      {
        "id": "uuid-1",
        "title": "项目会议",
        "date": "2025-12-02",
        "is_all_day": false,
        "start_time": "14:00",
        "end_time": "16:00",
        "location": "会议室A",
        "type_id": "general",
        "type_name": "General",
        "color": "#6B7280",
        "completed": false
      },
      {
        "id": "uuid-2",
        "title": "期末考试",
        "date": "2025-12-05",
        "is_all_day": true,
        "start_time": null,
        "end_time": null,
        "location": "教学楼",
        "type_id": "school",
        "type_name": "School",
        "color": "#22C55E",
        "completed": false
      }
    ],
    "date_range": {
      "start": "2025-12-02",
      "end": "2025-12-12"
    },
    "server_time": "2025-12-02T10:00:00Z"
  }
}
```

### 步骤 2: Agent 处理并返回提醒

#### API: `/agent/generate-reminders`

```http
POST /api/v1/agent/generate-reminders
Content-Type: application/json
Authorization: Bearer <token>

{
  "reminders": [
    {
      "id": "weather_1",
      "type": "weather",
      "title": "今日天气",
      "subtitle": "多云转晴，18°C - 25°C，适合外出"
    },
    {
      "id": "commute_1",
      "type": "commute",
      "title": "通勤提醒",
      "subtitle": "从大围到中文大学约需 25 分钟"
    },
    {
      "id": "important_1",
      "type": "important",
      "title": "重要提醒",
      "subtitle": "3天后有期末考试，记得复习！"
    }
  ]
}
```

#### Agent 需要返回的数据格式

> ⚠️ **重要**: Agent 只需要返回 `id`、`type`、`title`、`subtitle` 四个字段。
> **颜色由系统根据 `type` 自动设置**，无需传递颜色相关字段，避免增加出错风险。

```json
{
  "reminders": [
    {
      "id": "unique_id_1",
      "type": "weather",
      "title": "提醒标题",
      "subtitle": "提醒详情"
    },
    {
      "id": "unique_id_2",
      "type": "commute",
      "title": "提醒标题",
      "subtitle": "提醒详情"
    },
    {
      "id": "unique_id_3",
      "type": "important",
      "title": "提醒标题",
      "subtitle": "提醒详情"
    }
  ]
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ 是 | 提醒唯一标识 |
| `type` | string | ✅ 是 | 提醒类型：`weather`、`commute`、`important` |
| `title` | string | ✅ 是 | 提醒标题 |
| `subtitle` | string | ✅ 是 | 提醒详细内容 |

#### 提醒类型与颜色映射（系统自动处理）

| 类型 | 背景色 | 图标色 | 用途 |
|------|--------|--------|------|
| `weather` | #EAF4FD (浅蓝) | #60A5FA (蓝色) | 天气相关提醒 |
| `commute` | #E8F5E9 (浅绿) | #4ADE80 (绿色) | 通勤相关提醒 |
| `important` | #FCE4EC (浅粉) | #F472B6 (粉色) | 重要事项提醒 |

> 💡 如果 `type` 值不在上述三种之一，系统会自动使用 `important` 类型的颜色。

#### 超时与错误处理

| 场景 | 前端行为 |
|------|----------|
| Agent 响应成功且有数据 | 更新显示新的提醒内容 |
| Agent 响应超时（10秒） | 保持显示之前的提醒内容 |
| Agent 返回空数组 | 保持显示之前的提醒内容 |
| 网络错误或其他异常 | 保持显示之前的提醒内容 |

> 📝 **初始状态**: 在 Agent 首次成功响应之前，系统显示静态示例提醒：
> - 今日天气：多云转晴，18°C - 25°C，适合外出
> - 通勤信息：前往学校约需 25 分钟，距离 8.5 公里
> - 重要提醒：明天是 Kai 的生日，记得准备礼物 🎁

#### 响应
```json
{
  "success": true,
  "data": [
    {
      "id": "weather_1",
      "type": "weather",
      "title": "今日天气",
      "subtitle": "多云转晴，18°C - 25°C，适合外出",
      "bg_color": "#EAF4FD",
      "icon_bg": "#60A5FA"
    },
    {
      "id": "commute_1",
      "type": "commute",
      "title": "通勤提醒",
      "subtitle": "从大围到中文大学约需 25 分钟",
      "bg_color": "#E8F5E9",
      "icon_bg": "#4ADE80"
    },
    {
      "id": "important_1",
      "type": "important",
      "title": "重要提醒",
      "subtitle": "3天后有期末考试，记得复习！",
      "bg_color": "#FCE4EC",
      "icon_bg": "#F472B6"
    }
  ],
  "server_time": "2025-12-02T10:00:00Z"
}
```

### Agent 实现示例 (Python)

> ⚠️ **注意**: Agent 只需返回 `id`、`type`、`title`、`subtitle` 四个字段，**无需返回颜色**。

```python
import requests
from datetime import datetime

def generate_reminders(context: dict) -> dict:
    """
    基于上下文数据生成智能提醒
    
    context 包含：
    - user: 用户信息（home_address, school_address）
    - current_location: 当前位置
    - events: 未来10天的事件列表
    
    返回格式：
    {
        "reminders": [
            {"id": "xxx", "type": "weather|commute|important", "title": "标题", "subtitle": "内容"},
            ...
        ]
    }
    
    注意：
    - 只需返回 id, type, title, subtitle 四个字段
    - 颜色由后端根据 type 自动设置，无需传递
    - type 必须是 weather/commute/important 之一
    """
    
    reminders = []
    
    # 1. 生成天气提醒
    weather_reminder = generate_weather_reminder(context.get("current_location"))
    if weather_reminder:
        reminders.append(weather_reminder)
    
    # 2. 生成通勤提醒
    commute_reminder = generate_commute_reminder(
        context.get("current_location"),
        context.get("user", {}).get("home_address"),
        context.get("user", {}).get("school_address")
    )
    if commute_reminder:
        reminders.append(commute_reminder)
    
    # 3. 生成重要事项提醒
    important_reminder = generate_important_reminder(context.get("events", []))
    if important_reminder:
        reminders.append(important_reminder)
    
    return {"reminders": reminders}


def generate_weather_reminder(location: dict) -> dict:
    """
    生成天气提醒
    
    返回格式（只需4个字段，无需颜色）：
    {"id": "xxx", "type": "weather", "title": "标题", "subtitle": "内容"}
    """
    if not location:
        return {
            "id": "weather_default",
            "type": "weather",
            "title": "今日天气",
            "subtitle": "请开启定位获取天气信息"
        }
    
    # 调用天气 API
    # weather = get_weather(location["latitude"], location["longitude"])
    
    return {
        "id": f"weather_{datetime.now().strftime('%Y%m%d')}",
        "type": "weather",
        "title": "今日天气",
        "subtitle": "多云转晴，18°C - 25°C，适合外出"
    }


def generate_commute_reminder(location: dict, home: str, school: str) -> dict:
    """
    生成通勤提醒
    
    返回格式（只需4个字段，无需颜色）：
    {"id": "xxx", "type": "commute", "title": "标题", "subtitle": "内容"}
    """
    if not home and not school:
        return {
            "id": "commute_default",
            "type": "commute",
            "title": "通勤信息",
            "subtitle": "请在设置中填写家庭和学校地址"
        }
    
    # 调用地图 API 计算距离
    # distance = calculate_distance(location, school)
    
    return {
        "id": f"commute_{datetime.now().strftime('%Y%m%d')}",
        "type": "commute",
        "title": "通勤提醒",
        "subtitle": f"从{home}到{school}约需 25 分钟"
    }


def generate_important_reminder(events: list) -> dict:
    """
    基于事件生成重要提醒
    
    返回格式（只需4个字段，无需颜色）：
    {"id": "xxx", "type": "important", "title": "标题", "subtitle": "内容"}
    """
    if not events:
        return {
            "id": "important_default",
            "type": "important",
            "title": "重要提醒",
            "subtitle": "暂无重要事项，好好享受今天！"
        }
    
    # 分析事件，找出最重要的提醒
    today = datetime.now().date()
    
    for event in events:
        event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
        days_diff = (event_date - today).days
        
        if days_diff <= 3:  # 3天内的重要事件
            return {
                "id": f"important_{event['id']}",
                "type": "important",
                "title": "重要提醒",
                "subtitle": f"{'今天' if days_diff == 0 else f'{days_diff}天后'}有{event['title']}"
            }
    
    return {
        "id": "important_upcoming",
        "type": "important",
        "title": "重要提醒",
        "subtitle": f"接下来10天有 {len(events)} 个待办事项"
    }
```

---

## Agent 配置指南

### 方式 1: 直接修改后端

在 `backend/api/views.py` 中的各个 Agent 端点内添加调用外部 AI 服务的代码：

```python
# 在 agent_parse_task 函数中添加
import requests

AGENT_SERVICE_URL = "http://your-agent-service:8001"

@api_view(['POST'])
def agent_parse_task(request):
    user = request.user
    user_input = request.data.get('user_input', '')
    
    # 调用外部 Agent 服务
    try:
        agent_response = requests.post(
            f"{AGENT_SERVICE_URL}/parse-task",
            json={"user_input": user_input},
            timeout=10
        )
        parsed_data = agent_response.json()
    except Exception as e:
        # 如果 Agent 服务不可用，使用默认处理
        parsed_data = {"title": user_input}
    
    # 继续创建事件...
```

### 方式 2: 使用中间件代理

创建独立的 Agent 服务，后端通过配置文件指定 Agent 服务地址：

```python
# settings.py
AGENT_CONFIG = {
    'SERVICE_URL': os.environ.get('AGENT_SERVICE_URL', 'http://localhost:8001'),
    'TIMEOUT': 10,
    'ENABLED': os.environ.get('AGENT_ENABLED', 'false').lower() == 'true'
}
```

### 方式 3: 前端直接调用 Agent

前端可以先调用 Agent 服务，再将结果发送给后端：

```javascript
// 前端直接调用 Agent
const agentResponse = await fetch('http://agent-service:8001/parse-task', {
  method: 'POST',
  body: JSON.stringify({ user_input: text })
});
const parsed = await agentResponse.json();

// 然后调用后端创建事件
const result = await agentAPI.parseTask(parsed);
```

---

## 错误处理

### 标准错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  },
  "server_time": "2025-12-02T10:00:00Z"
}
```

### 常见错误代码

| 错误代码 | HTTP 状态码 | 说明 |
|----------|-------------|------|
| `VALIDATION_ERROR` | 400 | 请求数据验证失败 |
| `UNAUTHORIZED` | 401 | 未授权或 token 无效 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `AGENT_TIMEOUT` | 504 | Agent 服务超时 |
| `AGENT_ERROR` | 502 | Agent 服务返回错误 |

---

## 测试指南

### 使用 curl 测试

```bash
# 1. 登录获取 token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"account_id": "test@example.com"}' | jq -r '.data.access_token')

# 2. 测试 parse-task
curl -X POST http://localhost:8000/api/v1/agent/parse-task \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"user_input": "下午三点开会"}'

# 3. 测试 parse-calendar-type
curl -X POST http://localhost:8000/api/v1/agent/parse-calendar-type \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"user_input": "创建一个粉色的健身类型"}'

# 4. 测试 parse-event
curl -X POST http://localhost:8000/api/v1/agent/parse-event \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"user_input": "明天下午2点在图书馆学习"}'

# 5. 测试 reminder-context
curl -X GET http://localhost:8000/api/v1/agent/reminder-context \
  -H "Authorization: Bearer $TOKEN"

# 6. 测试 generate-reminders
curl -X POST http://localhost:8000/api/v1/agent/generate-reminders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "reminders": [
      {"id": "w1", "type": "weather", "title": "天气", "subtitle": "晴天"},
      {"id": "c1", "type": "commute", "title": "通勤", "subtitle": "25分钟"},
      {"id": "i1", "type": "important", "title": "提醒", "subtitle": "记得开会"}
    ]
  }'
```

### 使用 Python 测试

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 登录
login_res = requests.post(f"{BASE_URL}/auth/login", json={"account_id": "test@example.com"})
token = login_res.json()["data"]["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 测试各接口
def test_parse_task():
    res = requests.post(
        f"{BASE_URL}/agent/parse-task",
        json={"user_input": "下午三点开会"},
        headers=headers
    )
    print("parse-task:", res.json())

def test_parse_calendar_type():
    res = requests.post(
        f"{BASE_URL}/agent/parse-calendar-type",
        json={"user_input": "创建一个粉色的健身类型"},
        headers=headers
    )
    print("parse-calendar-type:", res.json())

def test_parse_event():
    res = requests.post(
        f"{BASE_URL}/agent/parse-event",
        json={"user_input": "明天下午2点在图书馆学习"},
        headers=headers
    )
    print("parse-event:", res.json())

def test_reminder_context():
    res = requests.get(f"{BASE_URL}/agent/reminder-context", headers=headers)
    print("reminder-context:", res.json())

def test_generate_reminders():
    res = requests.post(
        f"{BASE_URL}/agent/generate-reminders",
        json={
            "reminders": [
                {"id": "w1", "type": "weather", "title": "天气", "subtitle": "晴天"},
                {"id": "c1", "type": "commute", "title": "通勤", "subtitle": "25分钟"},
                {"id": "i1", "type": "important", "title": "提醒", "subtitle": "记得开会"}
            ]
        },
        headers=headers
    )
    print("generate-reminders:", res.json())

if __name__ == "__main__":
    test_parse_task()
    test_parse_calendar_type()
    test_parse_event()
    test_reminder_context()
    test_generate_reminders()
```

---

## 总结

| 功能 | 端点 | 用户操作 | Agent 返回 | 效果 |
|------|------|----------|------------|------|
| Add a Task for Today | `/agent/parse-task` | 输入自然语言 | 任务结构化数据 | **直接创建**事件到今天 |
| Create Calendar Type | `/agent/parse-calendar-type` | 输入描述 | 类型名称+颜色 | **填入表单**，用户确认 |
| Create Event | `/agent/parse-event` | 输入描述 | 完整事件信息 | **填入表单**，用户确认 |
| AI Reminder | `/agent/reminder-context` + `/agent/generate-reminders` | 点击刷新 | 3个提醒卡片 | **更新显示**（失败则保持原样） |

---

## 关键设计决策

### 1. AI Reminder 颜色处理
- **Agent 只需返回**: `id`, `type`, `title`, `subtitle`
- **颜色由后端自动设置**: 根据 `type` 值自动映射对应颜色
- **好处**: 减少 Agent 的复杂度和出错风险

### 2. 超时与容错机制
- **超时时间**: 10 秒
- **失败处理**: 保持显示之前的提醒数据，不影响用户体验
- **初始状态**: 显示静态示例数据，确保界面始终有内容

### 3. 数据刷新策略
- **刷新按钮**: 用户主动触发
- **加载动画**: 最少 1.5 秒，给用户视觉反馈
- **数据更新**: 仅在成功获取有效数据时更新

---

如有问题，请联系开发团队。

