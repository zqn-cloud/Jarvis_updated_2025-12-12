"""
Jarvis Agent Service
--------------------
对接 Jarvis 后端的 AI Agent 服务，提供以下端点：
  - POST /parse-task
  - POST /parse-calendar-type
  - POST /parse-event
  - POST /generate-reminders

运行示例：
  export JARVIS_API_BASE="http://localhost:8000/api/v1"
  export JARVIS_TOKEN="<后端登录获得的 Bearer token>"
  export OPENAI_API_BASE="https://xiaoai.plus/v1"    
  export OPENAI_API_KEY="<你的 key>"
  export OPENWEATHER_API_KEY="<你的 openweather key>"
  uvicorn backend.agent_service.main:app --host 0.0.0.0 --port 8001

Bear token 获得方式：
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"account_id": "你的账号"}'
"你的账号"例如jarvis@cuhk.com
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"account_id": "jarvis@cuhk.com"}'
输出的json文件当中的data.access_token就是Bearer token

依赖：
  pip install -r backend/agent_service/requirements.txt
"""

import json
import os
from datetime import datetime, timedelta, timezone
import logging
from typing import List, Optional

import requests
from fastapi import FastAPI, HTTPException
from openai import OpenAI, APIError
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


# ========= 环境配置 =========
JARVIS_API_BASE = os.getenv("JARVIS_API_BASE", "http://localhost:8000/api/v1")
JARVIS_TOKEN = os.getenv("JARVIS_TOKEN", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://xiaoai.plus/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_service")

# 北京时间时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

def beijing_now():
    """获取当前北京时间"""
    return datetime.now(BEIJING_TZ)

client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)
app = FastAPI(title="Jarvis Agent Service")

# 允许跨域，便于前端直接调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========= 数据模型 =========
class TextInput(BaseModel):
    user_input: str


class ReminderItem(BaseModel):
    id: str
    type: str
    title: str
    subtitle: str


class ReminderPayload(BaseModel):
    reminders: List[ReminderItem]


# ========= 工具函数 =========
def jarvis_request(path: str, *, method: str = "GET", payload: Optional[dict] = None):
    """调用 Jarvis 后端，自动附带 Bearer Token。"""
    headers = {
        "Authorization": f"Bearer {JARVIS_TOKEN}",
        "Content-Type": "application/json",
    }
    url = f"{JARVIS_API_BASE}{path}"
    try:
        resp = requests.request(method, url, headers=headers, json=payload, timeout=15)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"调用后端失败: {exc}") from exc

    if not resp.ok:
        # 把后端返回体一起带出去，便于调试
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    try:
        body = resp.json()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"后端返回非JSON: {resp.text}") from exc

    if "data" in body:
        return body["data"]
    return body


def llm_json(prompt: str) -> dict:
    """调用 LLM，要求返回 JSON 对象。"""
    try:
        res = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
    except APIError as exc:
        raise HTTPException(status_code=502, detail=f"LLM 调用失败: {exc}") from exc
    content = res.choices[0].message.content
    try:
        return json.loads(content)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"LLM JSON 解析失败: {content}") from exc


def safe_pick_type(type_id: Optional[str], available: List[dict]) -> str:
    valid_ids = [t["id"] for t in available]
    return type_id if type_id in valid_ids else "general"


def get_weather_summary(location: Optional[dict]) -> str:
    """使用 OpenWeather 获取简要天气。未配置或无定位则返回提示。"""
    if not OPENWEATHER_API_KEY:
        return "未配置天气 key"
    if not location:
        return "未获取到定位，无法查询天气"
    lat = location.get("latitude")
    lon = location.get("longitude")
    if lat is None or lon is None:
        return "定位信息不完整，无法查询天气"
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": "zh_cn"}
    url = "https://api.openweathermap.org/data/2.5/weather"
    try:
        resp = requests.get(url, params=params, timeout=8)
        data = resp.json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        advice = ""
        desc_lower = desc.lower()
        # 简单文案建议
        if any(k in desc_lower for k in ["雨", "rain", "drizzle", "storm"]):
            advice = "出门记得带伞，注意防滑"
        elif any(k in desc_lower for k in ["雪", "snow"]):
            advice = "道路湿滑，注意保暖和防滑"
        elif any(k in desc_lower for k in ["雷", "thunder"]):
            advice = "注意雷电天气，尽量避免户外停留"
        elif any(k in desc_lower for k in ["雾", "fog", "霾", "haze"]):
            advice = "能见度低，出行请减速，必要时佩戴口罩"
        elif temp >= 32:
            advice = "高温注意防暑，多喝水少暴晒"
        elif temp >= 28:
            advice = "天气较热，注意防晒补水"
        elif temp <= 5:
            advice = "低温注意保暖，出门加衣"
        elif temp <= 12:
            advice = "有点凉，出门注意加件外套"
        else:
            advice = "天气适宜，适合外出"

        return f"{desc}，约 {temp:.0f}°C，{advice}"
    except Exception:
        return "天气查询失败"


def get_commute_summary() -> str:
    """
    调用后端占位通勤接口，返回简要通勤信息。
    后端暂时返回固定路线，如失败则提供兜底。
    """
    try:
        data = jarvis_request("/location/commute", method="GET")
        origin = data.get("from", {})
        dest = data.get("to", {})
        routes = data.get("routes") or []
        if routes:
            r0 = routes[0]
            dur = r0.get("duration_minutes")
            dist = r0.get("distance_km")
            traffic = r0.get("traffic_status") or ""
            o_addr = origin.get("address") or origin.get("type") or "出发地"
            d_addr = dest.get("address") or dest.get("type") or "目的地"
            parts = []
            if dist:
                parts.append(f"{dist:.1f}km")
            if dur:
                parts.append(f"{dur}分钟")
            if traffic:
                parts.append(f"路况{traffic}")
            detail = " / ".join(parts) if parts else "路况信息暂无"
            return f"{o_addr} → {d_addr}，约 {detail}"
    except Exception:
        pass
    return "请预留 25 分钟出行"


# ========= 路由 =========
@app.get("/health")
def health():
    return {"status": "ok", "time": beijing_now().isoformat()}

# 显式处理预检请求，避免 405
@app.options("/{full_path:path}")
def options_any(full_path: str):
    return {}


def _extract_time(user_input: str):
    """
    尝试从中文/数字中提取时间，返回 (HH:MM, HH:MM) 或 (None, None)
    规则：
      - 匹配 “下午/晚上/pm” 则 +12（12点除外）
      - 默认时长 60 分钟
      - 支持中文数字（六点、七点半）
      - 支持时间范围：“3点到5点”、“3:00-5:00”
    """
    import re

    text = user_input.lower()
    hour = None
    minute = 0
    end_hour = None
    end_minute = 0

    def cn_num_to_int(s: str) -> Optional[int]:
        mapping = {'零': 0, '〇': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5,
                   '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
        if not s:
            return None
        if s.isdigit():
            return int(s)
        # 处理中文数字（十、十一、二十三）
        total = 0
        if s == '十':
            return 10
        if len(s) == 2 and s[0] == '十':
            # 十一、十二
            return 10 + mapping.get(s[1], 0)
        if len(s) == 2 and s[1] == '十':
            # 二十、三十
            return mapping.get(s[0], 0) * 10
        if len(s) == 3 and s[1] == '十':
            # 二十三
            return mapping.get(s[0], 0) * 10 + mapping.get(s[2], 0)
        if s in mapping:
            return mapping[s]
        return None

    def apply_meridiem(h: int, mer: str) -> int:
        if mer and (('下午' in mer) or ('晚上' in mer) or ('pm' in mer)):
            if h != 12:
                h = (h + 12) % 24
        return h

    # 0) 范围：HH:MM 到 HH:MM
    m_range_hhmm = re.search(r'(\d{1,2})[:：](\d{2})\s*(到|至|-|~)\s*(\d{1,2})[:：](\d{2})', text)
    if m_range_hhmm:
        h1, m1, h2, m2 = int(m_range_hhmm.group(1)), int(m_range_hhmm.group(2)), int(m_range_hhmm.group(4)), int(m_range_hhmm.group(5))
        hour, minute, end_hour, end_minute = h1, m1, h2, m2
    else:
        # 1) 范围：中文/数字 + 可选半，带可选上午/下午
        m_range_cn = re.search(
            r'(上午|早上|中午|下午|晚上|pm|am)?\s*([零〇一二两三四五六七八九十\d]{1,3})点(半)?\s*(到|至|-|~)\s*(上午|早上|中午|下午|晚上|pm|am)?\s*([零〇一二两三四五六七八九十\d]{1,3})点(半)?',
            text
        )
        if m_range_cn:
            mer1 = m_range_cn.group(1) or ''
            raw1 = m_range_cn.group(2)
            half1 = m_range_cn.group(3) is not None
            mer2 = m_range_cn.group(5) or mer1  # 第二段未写上午/下午则沿用第一段
            raw2 = m_range_cn.group(6)
            half2 = m_range_cn.group(7) is not None
            num1 = cn_num_to_int(raw1)
            num2 = cn_num_to_int(raw2)
            try:
                if num1 is None:
                    num1 = int(raw1)
            except Exception:
                num1 = None
            try:
                if num2 is None:
                    num2 = int(raw2)
            except Exception:
                num2 = None
            if num1 is not None and num2 is not None:
                hour = apply_meridiem(num1, mer1)
                minute = 30 if half1 else 0
                end_hour = apply_meridiem(num2, mer2)
                end_minute = 30 if half2 else 0

    # 2) 单个时间（无范围）先匹配 HH:MM
    if hour is None:
        m = re.search(r'(\d{1,2})[:：](\d{2})', text)
        if m:
            hour = int(m.group(1))
            minute = int(m.group(2))
    # 3) 单个时间 中文/数字点(半)
    if hour is None:
        m2 = re.search(r'(上午|早上|中午|下午|晚上|pm|am)?\s*([零〇一二两三四五六七八九十\d]{1,3})点(半)?', text)
        if m2:
            meridiem = m2.group(1) or ''
            raw_num = m2.group(2)
            half = m2.group(3) is not None
            num = cn_num_to_int(raw_num)
            if num is None:
                try:
                    num = int(raw_num)
                except Exception:
                    num = None
            hour = num
            minute = 30 if half else 0
            hour = apply_meridiem(hour, meridiem) if hour is not None else None

    if hour is None or hour > 23:
        return None, None
    if end_hour is None:
        end_hour = (hour + 1) % 24
        end_minute = minute
    start = f"{hour:02d}:{minute:02d}"
    end = f"{end_hour:02d}:{end_minute:02d}"
    return start, end


def _keyword_fallback(user_input: str):
    """
    关键词兜底：当正则未匹配到时间时，根据语义给出大致时间段。
    """
    text = user_input
    if any(k in text for k in ['晚上', '夜里', '夜间']):
        return "18:00", "19:00"
    if '下午' in text:
        return "15:00", "16:00"
    if '中午' in text:
        return "12:00", "13:00"
    if any(k in text for k in ['早上', '上午', '早晨']):
        return "09:00", "10:00"
    return None, None


@app.post("/parse-task")
def parse_task(body: TextInput):
    user_input = body.user_input
    # 阶段1：获取上下文
    ctx = jarvis_request("/agent/parse-task", method="POST", payload={"user_input": user_input})
    available_types = ctx["available_types"]
    type_opts = ", ".join(f'{t["id"]}({t["name"]})' for t in available_types)

    prompt = f"""
提取任务字段，日期固定今天（无需返回date）。
type_id 必须从: {type_opts}
输入: {user_input}
输出 JSON:
{{
  "title": "任务标题",
  "is_all_day": true/false,
  "start_time": "HH:MM 或 null",
  "end_time": "HH:MM 或 null",
  "location": "地点或空字符串",
  "type_id": "可选项中的id"
}}
"""
    parsed = llm_json(prompt)
    parsed["type_id"] = safe_pick_type(parsed.get("type_id"), available_types)

    # 无论 LLM 是否返回时间，都尝试从原文本再解析一遍，若解析到则覆盖/补全
    start, end = _extract_time(user_input)
    if not start:
        ks, ke = _keyword_fallback(user_input)
        start = start or ks
        end = end or ke
    if start or end:
        parsed["is_all_day"] = False
        if start:
            parsed["start_time"] = start
        if end:
            parsed["end_time"] = end
    else:
        # 最终兜底：仍未解析出时间时，按关键词或默认 18:00-19:00
        ks, ke = _keyword_fallback(user_input)
        parsed["is_all_day"] = False
        parsed["start_time"] = ks or "18:00"
        parsed["end_time"] = ke or "19:00"

    logger.info("[parse_task] user_input=%s parsed=%s", user_input, parsed)
    return jarvis_request("/agent/parse-task", method="POST", payload=parsed)


@app.post("/parse-calendar-type")
def parse_calendar_type(body: TextInput):
    user_input = body.user_input
    ctx = jarvis_request("/agent/parse-calendar-type", method="POST", payload={"user_input": user_input})
    colors = [c["value"].upper() for c in ctx["available_colors"]]
    # 名称/值/中文关键词 → 规范色值
    name_to_value = {c["name"].lower(): c["value"].upper() for c in ctx["available_colors"]}
    synonym_to_value = {
        "粉": name_to_value.get("pink"),
        "粉色": name_to_value.get("pink"),
        "pink": name_to_value.get("pink"),
        "蓝": name_to_value.get("blue"),
        "蓝色": name_to_value.get("blue"),
        "blue": name_to_value.get("blue"),
        "绿": name_to_value.get("green"),
        "绿色": name_to_value.get("green"),
        "green": name_to_value.get("green"),
        "紫": name_to_value.get("purple"),
        "紫色": name_to_value.get("purple"),
        "purple": name_to_value.get("purple"),
        "红": name_to_value.get("red"),
        "红色": name_to_value.get("red"),
        "red": name_to_value.get("red"),
        "黄": name_to_value.get("amber"),
        "黄色": name_to_value.get("amber"),
        "橙": name_to_value.get("amber"),
        "橙色": name_to_value.get("amber"),
        "amber": name_to_value.get("amber"),
    }

    prompt = f"""
从描述中生成日历类型。
color 必须精确从列表选择: {", ".join(colors)}
输入: {user_input}
输出 JSON:
{{"name": "类型名称", "color": "#HEX"}}
"""
    parsed = llm_json(prompt)
    color_raw = parsed.get("color", "")
    color_upper = color_raw.upper()

    def pick_color() -> str:
        # 1) 直接是合法色值
        if color_upper in colors:
            return color_upper
        # 2) 名称匹配
        lower = color_raw.lower()
        if lower in name_to_value:
            return name_to_value[lower]
        # 3) 文本关键词匹配
        text = user_input.lower()
        for kw, val in synonym_to_value.items():
            if val and kw in text:
                return val
        # 4) 默认首个颜色
        return colors[0]

    color = pick_color()
    body = {"name": parsed.get("name", "默认类型"), "color": color}
    logger.info("[parse_calendar_type] user_input=%s parsed=%s final=%s", user_input, parsed, body)
    return jarvis_request("/agent/parse-calendar-type", method="POST", payload=body)


@app.post("/parse-event")
def parse_event(body: TextInput):
    user_input = body.user_input
    ctx = jarvis_request("/agent/parse-event", method="POST", payload={"user_input": user_input})
    available_types = ctx["available_types"]
    current_date = ctx.get("current_date")
    type_opts = ", ".join(f'{t["id"]}({t["name"]})' for t in available_types)

    prompt = f"""
解析事件（当前日期 {current_date}）。
type_id 必须从: {type_opts}
输入: {user_input}
输出 JSON:
{{
  "title": "事件标题",
  "date": "YYYY-MM-DD",
  "is_all_day": true/false,
  "start_time": "HH:MM 或 null",
  "end_time": "HH:MM 或 null",
  "location": "地点或空字符串",
  "type_id": "可选项中的id"
}}
"""
    parsed = llm_json(prompt)
    parsed["type_id"] = safe_pick_type(parsed.get("type_id"), available_types)
    # 默认日期：如果未给出，则使用 current_date
    if not parsed.get("date"):
        parsed["date"] = current_date
    # 无论 LLM 是否返回时间，都尝试从原文本再解析一遍，若解析到则覆盖/补全
    start, end = _extract_time(user_input)
    if not start:
        ks, ke = _keyword_fallback(user_input)
        start = start or ks
        end = end or ke
    if start or end:
        parsed["is_all_day"] = False
        if start:
            parsed["start_time"] = start
        if end:
            parsed["end_time"] = end
    else:
        # 最终兜底：仍未解析出时间时，按关键词或默认 18:00-19:00
        ks, ke = _keyword_fallback(user_input)
        parsed["is_all_day"] = False
        parsed["start_time"] = ks or "18:00"
        parsed["end_time"] = ke or "19:00"
    logger.info("[parse_event] user_input=%s parsed=%s", user_input, parsed)
    return jarvis_request("/agent/parse-event", method="POST", payload=parsed)


@app.post("/generate-reminders")
def generate_reminders():
    ctx = jarvis_request("/agent/reminder-context")
    location = ctx.get("current_location")
    events = ctx.get("events", [])
    weather_text = get_weather_summary(location)
    commute_text = get_commute_summary()
    important_text = "未来10天暂无行程"

    def summarize_events(evts: list) -> str:
        if not evts:
            return "未来10天暂无行程"
        try:
            today = beijing_now().date()
            end = today + timedelta(days=10)
            # 过滤：未完成、今天到10天内
            filtered = []
            for e in evts:
                if e.get("completed"):
                    continue
                d_raw = e.get("date")
                if not d_raw:
                    continue
                try:
                    d = datetime.fromisoformat(d_raw).date()
                except Exception:
                    continue
                if today <= d <= end:
                    filtered.append((d, e))
            if not filtered:
                # 尝试用所有事件中最近的一个做提醒，避免空文案
                candidates = []
                for e in evts:
                    d_raw = e.get("date")
                    if not d_raw:
                        continue
                    try:
                        d = datetime.fromisoformat(d_raw).date()
                    except Exception:
                        continue
                    candidates.append((d, e))
                candidates = [(d, e) for d, e in candidates if d >= today]
                if not candidates:
                    return "未来10天暂无行程"
                candidates.sort(key=lambda x: x[0])
                d, e = candidates[0]
                return f"最近行程：{fmt(e)}（{d}）"

            def fmt(e):
                t = e.get("start_time") or ""
                return f"{e['title']} {t}".strip()

            # 今天的行程
            today_list = [e for d, e in filtered if d == today]
            # 明天及之后
            future = [(d, e) for d, e in filtered if d > today]
            future.sort(key=lambda x: x[0])

            parts = []
            if today_list:
                if len(today_list) == 1:
                    parts.append(f"今天：{fmt(today_list[0])}")
                else:
                    titles = "、".join(fmt(e) for e in today_list[:2])
                    more = len(today_list)
                    more_text = f" 等{more}个" if more > 0 else ""
                    parts.append(f"今天有{len(today_list)}个：{titles}{more_text}")

            if future:
                first_date = future[0][0]
                same_day = [e for d, e in future if d == first_date]
                days_diff = (first_date - today).days
                when_text = "明天" if days_diff == 1 else f"{days_diff}天后"
                if len(same_day) == 1:
                    parts.append(f"{when_text}：{fmt(same_day[0])}（{first_date}）")
                else:
                    titles = "、".join(fmt(e) for e in same_day[:2])
                    more = len(same_day)
                    more_text = f" 等{more}个" if more > 0 else ""
                    parts.append(f"{when_text}有{len(same_day)}个：{titles}{more_text}")

            return "；".join(parts) if parts else "未来10天暂无行程"
        except Exception as exc:
            logger.error("[summarize_events] 异常: %s, events=%s", exc, evts[:3] if evts else [])
            # 尝试返回一个基本的提醒，而不是"查看近期行程"
            if evts:
                # 尝试找到第一个未完成的事件
                for e in evts:
                    if not e.get("completed") and e.get("title"):
                        return f"最近事件：{e.get('title')}"
            return "未来10天暂无行程"

    important_text = summarize_events(events)

    today_date = beijing_now().date()
    payload = {
        "reminders": [
            {
                "id": f"weather_{today_date}",
                "type": "weather",
                "title": "今日天气",
                "subtitle": weather_text,
            },
            {
                "id": f"commute_{today_date}",
                "type": "commute",
                "title": "通勤提醒",
                "subtitle": commute_text,
            },
            {
                "id": f"important_{today_date}",
                "type": "important",
                "title": "重要提醒",
                "subtitle": important_text,
            },
        ]
    }
    return jarvis_request("/agent/generate-reminders", method="POST", payload=payload)


