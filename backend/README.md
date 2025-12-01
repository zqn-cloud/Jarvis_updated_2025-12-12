# Jarvis Calendar Backend

Django REST API backend for Jarvis Calendar application.

## 技术栈

- Python 3.x
- Django 5.x
- Django REST Framework
- SQLite (数据库)
- django-cors-headers (跨域支持)

## 快速开始

### 1. 激活虚拟环境

```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# 或
source venv/bin/activate  # Linux/Mac
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行数据库迁移

```bash
python manage.py migrate
```

### 4. 启动开发服务器

```bash
python manage.py runserver
```

服务器将在 http://localhost:8000 启动。

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

## 管理后台

可以通过 Django Admin 管理数据：

1. 创建超级用户：
```bash
python manage.py createsuperuser
```

2. 访问 http://localhost:8000/admin/

