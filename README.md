# Jarvis Calendar

一个基于 Vue 3 + Django + FastAPI 的智能日程管理应用，集成 AI Agent 提供自然语言交互和智能提醒功能。

---

## 📁 项目结构

```
javix-1/
├── backend/                    # Django 后端
│   ├── api/                    # API 应用（精简后）
│   ├── agent_service/          # Agent Service (FastAPI)
│   │   ├── main.py             # FastAPI 应用
│   │   └── requirements.txt   # Agent 依赖
│   ├── jarvis_backend/         # 项目配置
│   ├── db.sqlite3              # 数据库
│   └── venv/                   # Python 环境
├── src/                        # Vue 前端（精简后）
│   ├── components/             # 仅保留使用中的组件
│   ├── services/api.js         # API 服务
│   ├── assets/main.css         # 样式
│   ├── App.vue                 # 主组件
│   └── main.js                 # 入口
├── index.html
├── package.json
├── package-lock.json
├── vite.config.js
├── README.md
├── API_DOCUMENTATION.md
├── AI_AGENT_INTEGRATION.md     # Agent 集成文档
└── cloudflared-windows-amd64.exe
```

---
此处以开发者文件夹位置作为示例，部署请自行更换

## 🚀 启动方式一：本地运行

适用于本地开发和测试。

### 前置要求

- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 首次运行：安装依赖

#### 安装前端依赖

```powershell
cd F:\AIMS5701\javix-1
npm install
```

#### 安装后端依赖（如果 venv 不存在）

```powershell
cd F:\AIMS5701\javix-1\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install django djangorestframework django-cors-headers
python manage.py migrate
python manage.py seed_demo  # 可选：填充示例数据
```

#### 安装 Agent Service 依赖（可选，用于 AI 功能）

```powershell
# 确保已激活虚拟环境
cd F:\AIMS5701\javix-1\backend
.\venv\Scripts\Activate.ps1
pip install -r agent_service/requirements.txt
```

**注意**：Agent Service 是可选的。如果不需要 AI 功能（自然语言解析、智能提醒），可以跳过此步骤。

### 日常启动步骤

#### 1. 启动后端（终端1）

```powershell
cd F:\AIMS5701\javix-1\backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

成功标志：`Starting development server at http://127.0.0.1:8000/`

#### 2. 启动 Agent Service（终端2，可选）

如果需要使用 AI 功能（自然语言解析、智能提醒），需要启动 Agent Service：

```powershell
# 设置环境变量（Windows PowerShell）
$env:JARVIS_API_BASE="http://localhost:8000/api/v1"
$env:JARVIS_TOKEN="<从后端登录获取的token>"
$env:OPENAI_API_BASE="https://xiaoai.plus/v1"
$env:OPENAI_API_KEY="<你的OpenAI API Key>"
$env:OPENWEATHER_API_KEY="<你的OpenWeather API Key>"  # 可选

# 启动 Agent Service
cd F:\AIMS5701\javix-1
.\venv\Scripts\Activate.ps1  # 如果还没激活
uvicorn backend.agent_service.main:app --host 0.0.0.0 --port 8001
```

成功标志：`Uvicorn running on http://0.0.0.0:8001`

**获取 Bearer Token**：
```powershell
# 先登录获取 token
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"account_id\": \"jarvis@cuhk.com\"}'
# 从响应的 data.access_token 中复制 token
```

**注意**：如果不需要 AI 功能，可以跳过此步骤，应用仍可正常使用。

#### 3. 启动前端（终端3）

```powershell
cd F:\AIMS5701\javix-1
npm run dev
```

成功标志：`Local: http://localhost:5173/`

#### 4. 访问应用

打开浏览器访问：**http://localhost:5173**

#### 4. index.html 配置（本地模式）

确保 `index.html` 中**没有**设置 `JARVIS_API_URL`（注释掉或删除）：

```html
<body>
  <div id="app"></div>
  <!-- 本地模式不需要这个 script -->
  <script type="module" src="/src/main.js"></script>
</body>
```

---

## 🌐 启动方式二：Cloudflare Tunnel（外网访问）

适用于让外部用户通过互联网访问你本地运行的应用。

### 前置要求

- 完成"本地运行"的所有前置要求
- 下载 [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)
- 将 `cloudflared-windows-amd64.exe` 放在项目目录下

### 步骤

#### 1. 启动后端（终端1）

```powershell
cd F:\AIMS5701\javix-1\backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

#### 2. 启动前端（终端2）

```powershell
cd F:\AIMS5701\javix-1
npm run dev
```

#### 3. 启动后端隧道（终端3）

```powershell
cd F:\AIMS5701\javix-1
.\cloudflared-windows-amd64.exe tunnel --url http://localhost:8000
```

**记录输出的 URL**，例如：`https://abc-def-123.trycloudflare.com`

#### 4. 修改 index.html（外网模式）

编辑 `index.html`，添加后端隧道地址（**注意要加 `/api/v1`**）：

```html
<body>
  <div id="app"></div>
  <script>
    window.JARVIS_API_URL = 'https://abc-def-123.trycloudflare.com/api/v1';
  </script>
  <script type="module" src="/src/main.js"></script>
</body>
```

保存后，在终端2按 `Ctrl+C` 停止前端，然后重新运行：

```powershell
npm run dev
```

#### 5. 启动前端隧道（终端4）

```powershell
cd F:\AIMS5701\javix-1
.\cloudflared-windows-amd64.exe tunnel --url http://localhost:5173
```

**记录输出的 URL**，例如：`https://xyz-789-abc.trycloudflare.com`

#### 6. 分享给外部用户

将**终端4输出的 URL** 发给别人，他们就可以访问你的应用了！

---

## 📊 启动检查清单

### 本地模式

| 检查项 | 状态 |
|--------|------|
| 后端运行在 localhost:8000 | ☐ |
| Agent Service 运行在 localhost:8001（可选） | ☐ |
| 前端运行在 localhost:5173 | ☐ |
| index.html 无 JARVIS_API_URL | ☐ |
| 浏览器访问 localhost:5173 | ☐ |

### Cloudflare 模式

| 检查项 | 状态 |
|--------|------|
| 后端运行在 localhost:8000 | ☐ |
| Agent Service 运行在 localhost:8001（可选） | ☐ |
| 前端运行在 localhost:5173 | ☐ |
| 后端隧道运行中 (终端3) | ☐ |
| index.html 设置了后端隧道 URL + `/api/v1` | ☐ |
| 前端重启 (npm run dev) | ☐ |
| 前端隧道运行中 (终端4) | ☐ |

---

## 🔑 测试账号

| 账号 | 说明 |
|------|------|
| `jarvis@cuhk.com` | 预置示例数据 |
| 任意邮箱格式 | 自动创建新账号 |

---

## 🛠 常见问题

### Q: 登录失败 "Login failed"

**原因**：前端无法连接后端

**解决**：
1. 检查后端是否在运行（终端1）
2. 本地模式：确保 index.html 没有设置 JARVIS_API_URL
3. 外网模式：确保 index.html 的 URL 包含 `/api/v1`

### Q: Cloudflare 报错 1033

**原因**：隧道无法连接到本地服务

**解决**：
1. 确保本地服务（前端/后端）正在运行
2. 先启动本地服务，再启动隧道

### Q: 外网访问时 API 调用失败

**原因**：index.html 中的后端地址配置错误

**解决**：
1. 确认后端隧道 URL 正确
2. **必须**在 URL 后加 `/api/v1`
3. 修改后重启前端

### Q: 每次重启隧道地址变了

**原因**：免费隧道每次启动会分配新地址

**解决**：
1. 更新 index.html 中的后端隧道地址
2. 重启前端
3. （可选）使用 Cloudflare 账号创建固定域名隧道

### Q: AI 功能不可用（自然语言解析、智能提醒）

**原因**：Agent Service 未启动或配置错误

**解决**：
1. 确认 Agent Service 正在运行（http://localhost:8001）
2. 检查环境变量是否正确设置（JARVIS_TOKEN、OPENAI_API_KEY）
3. 验证 Bearer Token 是否有效（未过期）
4. 查看 Agent Service 控制台的错误信息
5. 使用 `curl http://localhost:8001/health` 验证服务状态

**注意**：Agent Service 是可选的。如果未启动，应用仍可正常使用，但 AI 相关功能将不可用。

---

## 📚 API 文档

详细 API 文档见：[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

### 主要接口

| 功能 | 方法 | 端点 |
|------|------|------|
| 登录 | POST | /api/v1/auth/login |
| 获取用户 | GET | /api/v1/user |
| 事件列表 | GET | /api/v1/events |
| 创建事件 | POST | /api/v1/events |
| 日历类型 | GET | /api/v1/calendar-types |
| Agent 信息 | GET | /api/v1/agent/info |
| Agent 操作 | POST | /api/v1/agent/action |

### Agent API（AI 功能）

| 功能 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 解析今日任务 | POST | /api/v1/agent/parse-task | 自然语言 → 创建今日任务 |
| 解析日历类型 | POST | /api/v1/agent/parse-calendar-type | 描述 → 类型名称+颜色 |
| 解析事件 | POST | /api/v1/agent/parse-event | 描述 → 完整事件信息 |
| 获取提醒上下文 | GET | /api/v1/agent/reminder-context | 获取位置、地址、行程数据 |
| 生成智能提醒 | POST | /api/v1/agent/generate-reminders | 生成天气、通勤、重要提醒 |

> **注意**：Agent API 需要 Agent Service 运行在 http://localhost:8001。详细文档请参考 [AI_AGENT_INTEGRATION.md](./AI_AGENT_INTEGRATION.md)。

---

## 📝 开发说明

### 技术栈

- **前端**：Vue 3 + Vite + date-fns + lucide-vue-next
- **后端**：Django 5 + Django REST Framework
- **Agent Service**：FastAPI + OpenAI API + OpenWeather API（可选）
- **数据库**：SQLite
- **认证**：自定义 Token 认证

### Agent Service 配置

Agent Service 是一个独立的 FastAPI 微服务，提供 AI 功能。详细配置说明请参考：
- [backend/README.md](./backend/README.md) - 后端和 Agent Service 详细文档
- [AI_AGENT_INTEGRATION.md](./AI_AGENT_INTEGRATION.md) - Agent 集成完整文档

### 重新初始化数据库

```powershell
cd F:\AIMS5701\javix-1\backend
.\venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py seed_demo  # 填充示例数据
```

---

## 📄 License

MIT License
