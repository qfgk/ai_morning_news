# 早报机器人对接 API 文档

## 概述

本文档面向机器人开发者，说明如何调用早报系统 API 获取数据。

## 基础信息

- **Base URL**: `http://your-server.com:8080` 或 `https://your-domain.com`
- **Content-Type**: `application/json`
- **认证方式**: X-API-Key 请求头

## API 接口

### 1. 获取最新早报

**接口地址**: `GET /api/v1/briefing/latest`

**请求头**:
```http
X-API-Key: your-api-key
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "date": "2026-01-14",
    "title": "2026年1月14日 早报",
    "ai_summary": "今日科技新闻汇总...",
    "full_text": "# 2026年1月14日 早报\n\n📅 日期: 2026-01-14\n📰 文章数: 10篇\n\n## 📋 今日摘要\n今日科技新闻汇总...\n\n## 🔥 热点文章\n### 1. 文章标题\n摘要内容...\n🔗 [查看原文](https://...)\n...",
    "total_count": 10,
    "articles": [
      {
        "id": 1,
        "title": "文章标题",
        "summary": "文章摘要内容",
        "source_url": "https://example.com/article",
        "source_type": "aibase",
        "publication_date": "2026-01-14",
        "created_at": "2026-01-14T08:00:00"
      }
    ]
  }
}
```

**cURL 示例**:
```bash
curl -X GET http://your-server.com:8080/api/v1/briefing/latest \
  -H "X-API-Key: your-api-key"
```

---

### 2. 获取指定日期早报

**接口地址**: `GET /api/v1/briefing/{date}`

**路径参数**:
- `date`: 日期，格式 `YYYY-MM-DD`，例如 `2026-01-14`

**请求头**:
```http
X-API-Key: your-api-key
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "date": "2026-01-14",
    "title": "2026年1月14日 早报",
    "summary": "今日摘要...",
    "total_count": 10,
    "articles": [...]
  }
}
```

**cURL 示例**:
```bash
curl -X GET http://your-server.com:8080/api/v1/briefing/2026-01-14 \
  -H "X-API-Key: your-api-key"
```

---

### 3. 手动生成早报

**接口地址**: `POST /api/v1/briefing/generate`

**请求头**:
```http
X-API-Key: your-api-key
Content-Type: application/json
```

**请求体**:
```json
{
  "date": "2026-01-14",
  "sources": ["aibase"],
  "limit": 10,
  "use_cache": true,
  "save_to_db": true
}
```

**参数说明**:
- `date`: 日期（可选，默认今天）
- `sources`: 数据源列表（可选，默认 ["aibase"]）
- `limit`: 文章数量（可选，默认 10）
- `use_cache`: 是否使用缓存（可选，默认 true）
- `save_to_db`: 是否保存到数据库（可选，默认 false）

**响应示例**:
```json
{
  "code": 200,
  "message": "早报生成成功",
  "data": {
    "date": "2026-01-14",
    "title": "2026年1月14日 早报",
    "summary": "...",
    "total_count": 10,
    "articles": [...]
  }
}
```

**cURL 示例**:
```bash
curl -X POST http://your-server.com:8080/api/v1/briefing/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'
```

---

### 4. 分页查询早报列表

**接口地址**: `GET /api/v1/briefing/list`

**请求参数**:
- `limit`: 每页数量（可选，默认 10，最大 100）
- `offset`: 偏移量（可选，默认 0）

**请求头**:
```http
X-API-Key: your-api-key
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "briefings": [
      {
        "id": 1,
        "date": "2026-01-14",
        "title": "2026年1月14日 早报",
        "total_count": 10
      }
    ],
    "count": 1,
    "limit": 10,
    "offset": 0
  }
}
```

**cURL 示例**:
```bash
curl -X GET "http://your-server.com:8080/api/v1/briefing/list?limit=20&offset=0" \
  -H "X-API-Key: your-api-key"
```

---

## 数据模型

### 早报对象 (DailyBriefing)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 早报 ID |
| date | string | 日期 (YYYY-MM-DD) |
| title | string | 标题 |
| ai_summary | string | AI 生成的总体摘要 |
| full_text | string | **完整的格式化早报文本（可直接发送）** |
| total_count | int | 文章总数 |
| articles | array | 文章列表 |
| created_at | string | 创建时间 (ISO 8601) |

**⭐ 重点字段说明：`full_text`**

`full_text` 是一个**已经格式化好的完整早报文本**，可以直接发送给用户，无需自己组装。

格式示例：
```markdown
# 2026年1月14日 早报

📅 日期: 2026-01-14
📰 文章数: 10篇

## 📋 今日摘要
今日科技新闻汇总...

## 🔥 热点文章
### 1. 文章标题
摘要内容...
🔗 [查看原文](https://...)

### 2. 另一篇文章
摘要内容...
🔗 [查看原文](https://...)

---
_由 AI 智能生成于 2026-01-14_
```

**推荐用法**：
- **直接使用 full_text**：获取后直接发送给用户，无需任何处理
- **自定义组装**：使用 title、ai_summary、articles 字段自己组装

### 文章对象 (Article)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 文章 ID |
| title | string | 标题 |
| summary | string | AI 生成的摘要 |
| source_url | string | 原文链接 |
| source_type | string | 来源类型 (aibase/rss/api) |
| publication_date | string | 发布日期 |
| created_at | string | 创建时间 |

---

## 错误码

| Code | 说明 |
|------|------|
| 200 | 成功（包括暂无数据的情况） |
| 400 | 请求参数错误 |
| 401 | API Key 无效或缺失 |
| 403 | API Key 不正确 |
| 500 | 服务器错误 |

**注意**: 当暂无早报数据时，返回 **200 状态码**，而非 404。

**暂无数据响应示例**:
```json
{
  "code": 200,
  "message": "暂无本日早报数据",
  "data": null
}
```

**错误响应示例**:
```json
{
  "code": 401,
  "message": "缺少API密钥，请在请求头中添加 X-API-Key"
}
```

---

## 机器人集成示例

### Python 示例

```python
import requests

class MorningNewsBot:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}

    def get_latest_briefing(self):
        """获取最新早报"""
        url = f"{self.base_url}/api/v1/briefing/latest"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_briefing_by_date(self, date):
        """获取指定日期早报"""
        url = f"{self.base_url}/api/v1/briefing/{date}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def generate_briefing(self, **kwargs):
        """手动生成早报"""
        url = f"{self.base_url}/api/v1/briefing/generate"
        response = requests.post(
            url,
            headers=self.headers,
            json=kwargs
        )
        return response.json()


# 使用示例
bot = MorningNewsBot(
    base_url="http://your-server.com:8080",
    api_key="your-api-key"
)

# 获取最新早报
result = bot.get_latest_briefing()
if result["code"] == 200:
    briefing = result["data"]

    # ⭐ 方法 1: 直接使用 full_text（推荐）
    # 这是已经格式化好的完整文本，可以直接发送
    full_text = briefing.get("full_text")
    if full_text:
        print(full_text)  # 直接发送给用户
        # 发送到微信/钉钉/飞书等
        # send_to_wechat(full_text)
    else:
        print("暂无完整文本")

    print("\n" + "="*50 + "\n")

    # 方法 2: 使用 articles 列表自己组装
    print(f"标题: {briefing['title']}")
    print(f"文章数: {briefing['total_count']}")

    for article in briefing["articles"]:
        print(f"- {article['title']}")
```

### JavaScript/Node.js 示例

```javascript
class MorningNewsBot {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json'
        };
    }

    async getLatestBriefing() {
        const response = await fetch(
            `${this.baseUrl}/api/v1/briefing/latest`,
            { headers: this.headers }
        );
        return await response.json();
    }

    async getBriefingByDate(date) {
        const response = await fetch(
            `${this.baseUrl}/api/v1/briefing/${date}`,
            { headers: this.headers }
        );
        return await response.json();
    }

    async generateBriefing(options = {}) {
        const response = await fetch(
            `${this.baseUrl}/api/v1/briefing/generate`,
            {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(options)
            }
        );
        return await response.json();
    }
}

// 使用示例
const bot = new MorningNewsBot(
    'http://your-server.com:8080',
    'your-api-key'
);

// 获取最新早报
const result = await bot.getLatestBriefing();
if (result.code === 200) {
    const briefing = result.data;
    console.log(`标题: ${briefing.title}`);
    console.log(`文章数: ${briefing.total_count}`);

    briefing.articles.forEach(article => {
        console.log(`- ${article.title}`);
    });
}
```

---

## 最佳实践

### 1. 定时拉取

建议机器人每 5-10 分钟拉取一次最新早报：

```python
import time

while True:
    result = bot.get_latest_briefing()
    if result["code"] == 200:
        briefing = result["data"]
        # 处理早报数据
        process_briefing(briefing)

    # 等待 5 分钟
    time.sleep(300)
```

### 2. 缓存处理

记录已处理的早报日期，避免重复：

```python
processed_dates = set()

def process_briefing(briefing):
    date = briefing["date"]
    if date in processed_dates:
        print(f"已处理过 {date} 的早报，跳过")
        return

    # 处理早报
    send_to_users(briefing)
    processed_dates.add(date)
```

### 3. 错误重试

```python
import time
from requests.exceptions import RequestException

def get_latest_with_retry(max_retries=3):
    for i in range(max_retries):
        try:
            result = bot.get_latest_briefing()
            if result["code"] == 200:
                return result["data"]
        except RequestException as e:
            print(f"请求失败: {e}")
            if i < max_retries - 1:
                time.sleep(5)  # 等待 5 秒后重试
    return None
```

---

## 测试工具

### 在线测试

使用 Postman 或 cURL 快速测试：

```bash
# 测试获取最新早报
curl http://localhost:8080/api/v1/briefing/latest \
  -H "X-API-Key: Ehlhg3EbnofqYl5xQmB8W1McQweqX91P"
```

### 本地测试

```bash
# 启动服务
python run_api.py

# 另一个终端测试
curl http://localhost:8080/api/v1/briefing/latest \
  -H "X-API-Key: Ehlhg3EbnofqYl5xQmB8W1McQweqX91P"
```

---

## 注意事项

1. **API Key 安全**: 不要在代码中硬编码 API Key，使用环境变量
2. **速率限制**: 默认每分钟 10 次请求（可在配置中调整）
3. **数据格式**: 所有日期格式为 `YYYY-MM-DD`
4. **超时设置**: 建议设置请求超时时间为 30 秒
5. **错误处理**: 务必处理错误响应，避免机器人崩溃

---

## 常见问题

**Q: 早报什么时候更新？**
A: 默认每天 8:00 自动生成（可在 `.env` 中配置 `SCHEDULE_CRONTAB`）

**Q: 如何手动触发生成？**
A: 调用 `POST /api/v1/briefing/generate` 接口

**Q: 没有 API Key 可以访问吗？**
A: 不可以，所有接口都需要 X-API-Key 认证

**Q: 支持 WebSocket 推送吗？**
A: 暂不支持，建议使用定时轮询或 Webhook 推送

**Q: 如何提高速率限制？**
A: 修改 `.env` 中的 `RATE_LIMIT_PER_MINUTE` 配置

---

## 技术支持

如有问题，请查看：
- 项目仓库: https://github.com/qfgk/ai_morning_news
- 完整文档: `docs/WEBHOOK_GUIDE.md`
- API 示例: `examples/webhook_receiver_examples.py`
