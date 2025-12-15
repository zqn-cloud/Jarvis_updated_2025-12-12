# Jarvis Calendar Backend

Django REST API backend for Jarvis Calendar application.

## 技术栈

### Django Backend
- Python 3.x
- Django 5.x
- Django REST Framework
- SQLite (数据库)
- django-cors-headers (跨域支持)

### Agent Service (独立微服务)
- FastAPI
- OpenAI API (LLM)
- OpenWeather API (天气数据)
- uvicorn (ASGI 服务器)

## 快速开始

### Django Backend

#### 1. 激活虚拟环境

```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# 或
source venv/bin/activate  # Linux/Mac
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 运行数据库迁移

```bash
python manage.py migrate
```

#### 4. 启动开发服务器

```bash
python manage.py runserver
```

服务器将在 http://localhost:8000 启动。

### Agent Service (可选)

Agent Service 是一个独立的 FastAPI 微服务，提供 AI 功能（自然语言解析、智能提醒等）。

#### 1. 安装 Agent Service 依赖

```bash
# 确保已激活虚拟环境
pip install -r agent_service/requirements.txt
```

#### 2. 配置环境变量

```bash
# 设置后端 API 地址
export JARVIS_API_BASE="http://localhost:8000/api/v1"

# 获取 Bearer Token（从 Django 后端登录获取）
# 先登录获取 token:
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"account_id": "your_account@example.com"}'
# 从响应中获取 data.access_token，然后设置：
export JARVIS_TOKEN="<your_access_token>"

# 设置 OpenAI API（必需）
export OPENAI_API_BASE="https://xiaoai.plus/v1"  # 或其他 OpenAI 兼容 API
export OPENAI_API_KEY="<your_openai_api_key>"
export OPENAI_MODEL="gpt-4o-mini"  # 可选，默认 gpt-4o-mini

# 设置 OpenWeather API（可选，用于天气提醒）
export OPENWEATHER_API_KEY="<your_openweather_api_key>"
```

#### 3. 启动 Agent Service

```bash
# 在项目根目录运行
uvicorn backend.agent_service.main:app --host 0.0.0.0 --port 8001
```

服务器将在 http://localhost:8001 启动。

#### 4. 验证 Agent Service

```bash
# 健康检查
curl http://localhost:8001/health
```

**注意**: Agent Service 是可选的。如果未启动，前端仍可正常使用，但 AI 相关功能（自然语言解析、智能提醒）将不可用。

## API 端点

所有API都在 `/api/v1/` 路径下。

### 认证
- `POST /api/v1/auth/login` - 登录
- `POST /api/v1/auth/logout` - 登出

### 时间
- `GET /api/v1/time` - 获取服务器时间

### 用户
- `GET /api/v1/user` - 获取用户信息
- `PUT /api/v1/user` - 更新用户信息
- `GET /api/v1/user/location` - 获取位置
- `POST /api/v1/user/location` - 更新位置

### 日历类型
- `GET /api/v1/calendar-types` - 获取所有类型
- `POST /api/v1/calendar-types` - 创建类型
- `PUT /api/v1/calendar-types/<type_id>` - 更新类型
- `DELETE /api/v1/calendar-types/<type_id>` - 删除类型
- `PATCH /api/v1/calendar-types/<type_id>/visibility` - 切换可见性

### 事件
- `GET /api/v1/events` - 获取事件列表
- `POST /api/v1/events` - 创建事件
- `GET /api/v1/events/<event_id>` - 获取事件详情
- `PUT /api/v1/events/<event_id>` - 更新事件
- `DELETE /api/v1/events/<event_id>` - 删除事件
- `PATCH /api/v1/events/<event_id>/complete` - 切换完成状态
- `POST /api/v1/events/<event_id>/links` - 添加链接
- `DELETE /api/v1/events/<event_id>/links` - 删除链接

### 文件
- `POST /api/v1/files/upload` - 上传文件
- `DELETE /api/v1/files/<file_id>` - 删除文件

### 提醒
- `GET /api/v1/reminders` - 获取智能提醒 (占位数据)

### 通勤
- `GET /api/v1/location/commute` - 获取通勤信息 (占位数据)

### Agent API (AI 功能)
- `GET /api/v1/agent/reminder-context` - 获取 AI Reminder 上下文数据
- `POST /api/v1/agent/parse-task` - 解析并创建今日任务
- `POST /api/v1/agent/parse-calendar-type` - 解析日历类型
- `POST /api/v1/agent/parse-event` - 解析事件信息
- `POST /api/v1/agent/generate-reminders` - 生成智能提醒

> **注意**: Agent API 需要 Agent Service 运行在 http://localhost:8001。详细文档请参考 `AI_AGENT_INTEGRATION.md`。

## 认证

使用 Bearer Token 认证。登录后获取 `access_token`，在后续请求的 Header 中添加：

```
Authorization: Bearer <access_token>
```

## 数据库

使用 SQLite，数据库文件位于 `backend/db.sqlite3`。

## 前端连接

前端需要连接到 `http://localhost:8000/api/v1/`。

使用 `src/services/api.js` 提供的API服务进行调用。

## Agent Service 集成

Agent Service 是一个独立的 FastAPI 微服务，通过 HTTP 与 Django 后端通信。

### 架构说明

```
Vue Frontend → Django Backend → Agent Service
     ↓              ↓                  ↓
  用户界面      API 服务          AI 处理
```

### 工作流程

1. **前端** → **后端**: 用户输入自然语言
2. **后端** → **Agent**: 后端收集上下文数据，转发给 Agent Service
3. **Agent** → **后端**: Agent 解析后返回结构化数据
4. **后端** → **前端**: 后端处理数据并返回给前端

### Agent Service API 端点

Agent Service 运行在 `http://localhost:8001`，提供以下端点：

| 端点 | 方法 | 功能 |
|------|------|------|
| `/parse-task` | POST | 解析今日任务（自然语言 → 结构化数据） |
| `/parse-calendar-type` | POST | 解析日历类型（描述 → 名称+颜色） |
| `/parse-event` | POST | 解析事件信息（描述 → 完整事件数据） |
| `/generate-reminders` | POST | 生成智能提醒（天气、通勤、重要事项） |
| `/health` | GET | 健康检查 |

### 环境变量说明

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `JARVIS_API_BASE` | ✅ | Django 后端 API 地址，默认 `http://localhost:8000/api/v1` |
| `JARVIS_TOKEN` | ✅ | Bearer Token，从 Django 后端登录获取 |
| `OPENAI_API_BASE` | ✅ | OpenAI API 地址 |
| `OPENAI_API_KEY` | ✅ | OpenAI API Key |
| `OPENAI_MODEL` | ❌ | 使用的模型，默认 `gpt-4o-mini` |
| `OPENWEATHER_API_KEY` | ❌ | OpenWeather API Key（用于天气提醒） |

### 获取 Bearer Token

```bash
# 登录获取 token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"account_id": "your_account@example.com"}'

# 响应示例:
# {
#   "success": true,
#   "data": {
#     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#     ...
#   }
# }
```

### 完整启动流程（包含 Agent Service）

1. **启动 Django Backend** (终端1)
   ```bash
   cd backend
   source venv/bin/activate  # 或 .\venv\Scripts\Activate.ps1 (Windows)
   python manage.py runserver
   ```

2. **启动 Agent Service** (终端2)
   ```bash
   # 设置环境变量
   export JARVIS_API_BASE="http://localhost:8000/api/v1"
   export JARVIS_TOKEN="<your_token>"
   export OPENAI_API_KEY="<your_key>"
   
   # 启动服务
   uvicorn backend.agent_service.main:app --host 0.0.0.0 --port 8001
   ```

3. **启动前端** (终端3)
   ```bash
   npm run dev
   ```

### 详细文档

更多关于 Agent Service 的详细信息，请参考：
- `AI_AGENT_INTEGRATION.md` - 完整的 Agent 集成文档
- `AGENT_PRESENTATION.md` - Agent Service 技术介绍

## 管理后台

可以通过 Django Admin 管理数据：

1. 创建超级用户：
```bash
python manage.py createsuperuser
```

2. 访问 http://localhost:8000/admin/

## 项目结构

```
backend/
├── api/                    # Django API 应用
│   ├── views.py           # API 视图
│   ├── urls.py            # URL 路由
│   └── models.py          # 数据模型
├── agent_service/         # Agent Service (FastAPI)
│   ├── main.py            # FastAPI 应用主文件
│   └── requirements.txt   # Agent Service 依赖
├── jarvis_backend/        # Django 项目配置
│   ├── settings.py        # 项目设置
│   ├── urls.py            # 根 URL 配置
│   └── wsgi.py            # WSGI 配置
├── db.sqlite3             # SQLite 数据库
├── manage.py              # Django 管理脚本
├── requirements.txt       # Django 依赖
└── README.md              # 本文档
```

## 故障排查

### Agent Service 无法连接后端

1. 确认 Django Backend 正在运行（http://localhost:8000）
2. 检查 `JARVIS_API_BASE` 环境变量是否正确
3. 确认 `JARVIS_TOKEN` 有效（未过期）
4. 查看 Agent Service 日志中的错误信息

### Agent Service API 调用失败

1. 检查 OpenAI API Key 是否正确
2. 确认网络连接正常（可访问 OpenAI API）
3. 查看 Agent Service 控制台输出的错误信息
4. 使用 `/health` 端点验证服务状态

### 前端 AI 功能不可用

1. 确认 Agent Service 正在运行（http://localhost:8001）
2. 检查浏览器控制台是否有错误
3. 确认后端 Agent API 端点正常工作
4. 查看网络请求是否成功

