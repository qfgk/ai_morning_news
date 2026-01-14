# 智能早报系统

基于 Python 的智能早报生成系统，集成 AI 智能总结、多消息源爬取、Redis 缓存和定时任务，为企业和个人提供高效的信息聚合解决方案。

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 目录

- [功能特性](#功能特性)
- [技术架构](#技术架构)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [API 文档](#api-文档)
- [Docker 部署](#docker-部署)
- [定时任务](#定时任务)
- [扩展开发](#扩展开发)
- [常见问题](#常见问题)
- [许可证](#许可证)

## 功能特性

### 核心功能

- 🌐 **多消息源支持**：适配器模式，支持 AIbase、RSS、API 等多种消息源
- 🤖 **AI 智能总结**：支持任何兼容 OpenAI 格式的大模型，自动生成文章摘要和每日汇总
- ⚡ **高性能并发**：异步爬虫 + 并发 AI 总结，可配置并发数（默认 3-10 个并行请求）
- 💾 **多级缓存**：Redis 缓存 + MySQL 持久化，提升响应速度
- 🚀 **RESTful API**：完整的 Web API，支持多种客户端集成
- ⏰ **定时任务**：基于 Celery Beat，支持 crontab 表达式灵活配置
- 🔒 **API 安全认证**：X-API-Key 密钥验证，保护接口安全

### 技术亮点

- 🎨 **领域驱动设计**：清晰分层架构（适配器层、服务层、仓储层、缓存层）
- 🔄 **异步处理**：基于 asyncio 的高性能异步爬虫
- 📦 **容器化部署**：支持 Docker Compose 一键部署
- 🗄️ **灵活数据库**：支持使用内部或外部 MySQL/Redis
- 📊 **任务监控**：完整的任务执行日志和状态跟踪
- 🌐 **模型无关**：统一使用 OpenAI API 格式，轻松切换不同 AI 提供商

## 技术架构

### 技术栈

| 类别 | 技术选型 | 版本要求 |
|------|---------|---------|
| **Web 框架** | Flask | 3.0+ |
| **异步爬虫** | crawl4ai, asyncio | - |
| **数据库** | MySQL / PostgreSQL | 8.0+ / 14+ |
| **ORM** | SQLAlchemy | 2.0 |
| **缓存** | Redis | 7.0+ |
| **任务队列** | Celery | 5.3+ |
| **AI 引擎** | OpenAI 格式 API | - |
| **配置管理** | Pydantic Settings | - |

### 系统架构

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Web API   │────▶│  Middleware  │────▶│  API Auth   │
└─────────────┘     └──────────────┘     └─────────────┘
       │
       ├─────────────┬──────────────┬──────────────┐
       ▼             ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Adapter  │  │ Service  │  │ Cache    │  │ Database │
│  Layer   │──│  Layer   │──│  Layer   │──│  Layer   │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
       │
       ▼
┌─────────────────────────────────────┐
│          Celery Tasks               │
│  ┌──────────┐      ┌──────────┐   │
│  │  Worker  │◀────▶│   Beat   │   │
│  └──────────┘      └──────────┘   │
└─────────────────────────────────────┘
```

## 项目结构

```
PythonProject/
├── api/                      # Flask Web API
│   ├── app.py               # 应用工厂
│   ├── routes/              # 路由模块
│   ├── schemas/             # Pydantic 数据模式
│   └── middleware/          # 中间件（认证、错误处理）
│
├── adapters/                 # 消息源适配器层
│   ├── base.py              # 抽象基类
│   ├── aibase_adapter.py    # AIbase 适配器
│   └── factory.py           # 适配器工厂
│
├── cache/                    # 缓存层
│   ├── redis_client.py      # Redis 客户端封装
│   ├── cache_keys.py        # 缓存键管理
│   └── cache_repository.py  # 缓存仓储
│
├── config/                   # 配置管理
│   ├── settings.py          # 主配置（Pydantic）
│   └── celery_config.py     # Celery 配置
│
├── core/                     # 核心模块
│   ├── models.py            # 领域模型（Pydantic）
│   └── constants.py         # 常量定义
│
├── database/                 # 数据库层
│   ├── base.py              # 数据库连接管理
│   └── models.py            # SQLAlchemy ORM 模型
│
├── repositories/             # 数据访问层
│   └── news_repository.py   # 新闻仓储
│
├── services/                 # 业务逻辑层
│   ├── ai_summary_service.py    # AI 总结服务
│   └── news_service.py          # 新闻业务服务
│
├── tasks/                    # 后台任务
│   ├── celery_app.py        # Celery 应用实例
│   └── daily_generation.py  # 早报生成任务
│
├── scripts/                  # 工具脚本
│   ├── init_db.py           # 数据库初始化
│   └── generate_api_key.py  # API 密钥生成
│
├── utils/                    # 工具函数
│   └── validation.py        # 数据验证
│
├── run_system.py             # 直接生成早报（命令行）
├── run_api.py                # 启动 Web API 服务
├── run_celery.py             # 启动 Celery Worker
├── run_beat.py               # 启动 Celery Beat
├── docker-compose.yml        # Docker Compose 配置
├── Dockerfile                # Docker 镜像构建
├── requirements.txt          # Python 依赖
├── .env                      # 环境变量（本地）
├── .env.docker.example       # 环境变量模板（Docker）
└── .gitignore                # Git 忽略文件
```

## 快速开始

### 前置要求

- Python 3.11+
- MySQL 8.0+ / PostgreSQL 14+（可选）
- Redis 7.0+（可选）

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/qfgk/ai_morning_news.git
cd ai_morning_news

# 安装 Python 依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
copy .env.example .env

# 编辑 .env 文件，配置必要参数
```

**最小配置示例：**

```bash
# AI 大模型配置（必填，选择一个）
AI_API_KEY=sk-your-api-key
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-3.5-turbo

# API 安全密钥（生产环境必填）
API_KEY=your-secret-api-key
```

**推荐配置：**

- 开发测试：使用 DeepSeek（性价比高）
- 生产环境：使用智谱AI 或 DeepSeek（国产稳定）
- 国际化：使用 OpenAI GPT 系列

### 3. 初始化数据库（可选）

```bash
python scripts/init_db.py
```

### 4. 运行系统

#### 方式一：命令行直接生成早报

```bash
# 基础模式（仅爬虫 + AI）
python run_system.py

# 启用数据库
python run_system.py --db

# 启用 Redis 缓存
python run_system.py --redis

# 完整模式（数据库 + 缓存）
python run_system.py --db --redis
```

#### 方式二：启动 Web API 服务

```bash
python run_api.py
```

访问 http://localhost:8080/health 检查服务状态。

#### 方式三：启动定时任务

需要启动两个服务：

```bash
# 终端 1：启动 Celery Worker（任务执行器）
python run_celery.py

# 终端 2：启动 Celery Beat（定时调度器）
python run_beat.py
```

## 配置说明

### 环境变量详解

#### 应用基础配置

```bash
DEBUG=True                           # 调试模式（生产环境设为 False）
ENVIRONMENT=development              # 环境：development/staging/production
FLASK_PORT=8080                      # API 服务端口
```

#### 数据库配置

```bash
# MySQL 连接字符串
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/morning_news

# 留空则不使用数据库
```

#### Redis 配置

```bash
REDIS_HOST=localhost                 # Redis 主机
REDIS_PORT=6379                      # Redis 端口
REDIS_PASSWORD=                      # Redis 密码（留空表示无密码）
REDIS_DB=0                           # Redis 数据库编号
```

#### Celery 配置

```bash
CELERY_BROKER_URL=redis://localhost:6379/1      # 消息队列
CELERY_RESULT_BACKEND=redis://localhost:6379/2  # 结果存储
```

#### AI 配置

```bash
# AI 大模型配置（必填）
AI_API_KEY=your_api_key               # API 密钥
AI_BASE_URL=https://api.openai.com/v1 # API 基础 URL
AI_MODEL=gpt-3.5-turbo                # 模型名称

# 并发配置
AI_SUMMARY_CONCURRENT=3               # AI 并发数（同时请求的数量）
```

**支持的 AI 提供商：**

本系统使用 OpenAI SDK，支持任何兼容 OpenAI API 格式的大模型：

| 提供商 | AI_BASE_URL | AI_MODEL | 推荐场景 |
|-------|------------|----------|---------|
| **OpenAI** | `https://api.openai.com/v1` | `gpt-3.5-turbo`, `gpt-4` | 国际通用 |
| **智谱AI** | `https://open.bigmodel.cn/api/paas/v4` | `glm-4.7`, `glm-4-plus` | 国产大模型 |
| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat` | 高性价比 |
| **通义千问** | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-turbo`, `qwen-plus` | 阿里云生态 |
| **Moonshot** | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` | Kimi |
| **百川** | `https://api.baichuan-ai.com/v1` | `Baichuan2` | 百川智能 |

**配置示例：**

```bash
# 示例 1: 使用 OpenAI GPT-3.5
AI_API_KEY=sk-your-openai-key
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-3.5-turbo

# 示例 2: 使用智谱AI GLM-4
AI_API_KEY=your-zhipuai-key
AI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
AI_MODEL=glm-4.7

# 示例 3: 使用 DeepSeek（推荐，性价比高）
AI_API_KEY=sk-your-deepseek-key
AI_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat

# 示例 4: 使用通义千问
AI_API_KEY=sk-your-qwen-key
AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL=qwen-turbo
```

**切换 AI 提供商：**

只需修改 `.env` 文件中的三个配置项，无需修改代码：

```bash
# 从 OpenAI 切换到 DeepSeek
AI_API_KEY=sk-deepseek-key
AI_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat
```

系统会自动使用新的配置，无需重启应用（仅在下次调用时生效）。

#### 爬虫配置

```bash
CRAWLER_TIMEOUT=30                    # 请求超时（秒）
CRAWLER_MAX_ARTICLES=10               # 每次最多抓取文章数
CRAWLER_DELAY=1.0                     # 请求间隔（秒）
```

#### 定时任务配置

```bash
# Crontab 表达式：分 时 日 月 周
SCHEDULE_CRONTAB=0 8 * * *            # 每天 8:00
```

#### API 安全配置

```bash
API_KEY=your_secret_key               # API 密钥（留空则不验证）
```

## API 文档

### 安全认证

所有 API 接口（除 `/health` 外）都需要在请求头中携带 API 密钥：

```http
X-API-Key: your_api_key_here
```

### 接口列表

#### 1. 健康检查

```http
GET /health
```

**无需认证**

**响应示例：**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-14T10:30:00Z"
}
```

#### 2. 获取最新早报

```http
GET /api/v1/briefing/latest
```

**需要认证**

**响应示例：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "date": "2025-01-14",
    "title": "早报 - 2025-01-14",
    "articles": [...],
    "total_count": 10,
    "ai_summary": "今日要闻..."
  }
}
```

#### 3. 获取指定日期早报

```http
GET /api/v1/briefing/<date>
```

**参数：**
- `date`: 日期，格式 `YYYY-MM-DD`

**示例：**
```bash
curl -H "X-API-Key: your_key" \
  http://localhost:8080/api/v1/briefing/2025-01-14
```

#### 4. 手动生成早报

```http
POST /api/v1/briefing/generate
Content-Type: application/json
```

**请求体：**
```json
{
  "date": "2025-01-14",
  "sources": ["aibase"],
  "limit": 10,
  "use_cache": true,
  "save_to_db": true
}
```

**参数说明：**
- `date`: 日期（可选，默认今天）
- `sources`: 消息源列表（可选，默认 ["aibase"]）
- `limit`: 文章数量（可选，默认 10）
- `use_cache`: 是否使用缓存（可选，默认 true）
- `save_to_db`: 是否保存到数据库（可选，默认 false）

#### 5. 早报列表

```http
GET /api/v1/briefing/list?limit=10&offset=0
```

**参数：**
- `limit`: 每页数量（可选，默认 10）
- `offset`: 偏移量（可选，默认 0）

### 错误响应

| 错误码 | 说明 |
|-------|------|
| 401 | 缺少 API 密钥 |
| 403 | API 密钥无效 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

**错误响应格式：**
```json
{
  "code": 401,
  "message": "缺少API密钥，请在请求头中添加 X-API-Key"
}
```

### 调用示例

#### Python

```python
import requests

headers = {"X-API-Key": "your_api_key"}
response = requests.get(
    "http://localhost:8080/api/v1/briefing/latest",
    headers=headers
)
print(response.json())
```

#### cURL

```bash
curl -H "X-API-Key: your_api_key" \
  http://localhost:8080/api/v1/briefing/latest
```

#### JavaScript

```javascript
fetch('http://localhost:8080/api/v1/briefing/latest', {
  headers: {'X-API-Key': 'your_api_key'}
})
.then(res => res.json())
.then(data => console.log(data));
```

## Docker 部署

### 快速部署

```bash
# 1. 复制环境变量模板
copy .env.docker.example .env

# 2. 编辑 .env，配置必要参数
# AI_API_KEY=your_api_key
# AI_BASE_URL=your_ai_base_url
# AI_MODEL=your_model_name
# API_KEY=your_secret_key

# 3. 启动服务
docker-compose up -d

# 4. 查看状态
docker-compose ps
```

### 部署模式

#### 模式一：使用 Docker 内部数据库（推荐新手）

```bash
docker-compose --profile mysql --profile redis up -d
```

启动所有服务，包括 MySQL 和 Redis 容器。

#### 模式二：使用外部数据库（推荐生产环境）

```bash
# 1. 修改 .env，配置外部数据库
DATABASE_URL=mysql+pymysql://user:pass@external_host:3306/morning_news
REDIS_HOST=external_redis_host
CELERY_BROKER_URL=redis://external_redis_host:6379/1
CELERY_RESULT_BACKEND=redis://external_redis_host:6379/2

# 2. 启动应用服务（不启动数据库容器）
docker-compose up -d
```

#### 模式三：混合模式

```bash
# 仅使用内部 MySQL
docker-compose --profile mysql up -d

# 仅使用内部 Redis
docker-compose --profile redis up -d
```

### 服务说明

| 服务 | 容器名 | 端口 | Profile | 说明 |
|------|--------|------|---------|------|
| Web API | morning_news_web | 8080 | - | RESTful API 服务 |
| MySQL | morning_news_db | 3306 | mysql | 关系型数据库（可选） |
| Redis | morning_news_redis | 6379 | redis | 缓存（可选） |
| Celery Worker | morning_news_celery_worker | - | - | 异步任务执行器 |
| Celery Beat | morning_news_celery_beat | - | - | 定时任务调度器 |

### 常用命令

```bash
# 查看日志
docker-compose logs -f web

# 重启服务
docker-compose restart web

# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 进入容器
docker-compose exec web bash

# 初始化数据库
docker-compose exec web python scripts/init_db.py

# 手动生成早报
docker-compose exec web python run_system.py --db

# 重新构建镜像
docker-compose build
```

### 健康检查

```bash
# 检查 API 服务
curl http://localhost:8080/health

# 检查数据库连接（仅限内部 MySQL）
docker-compose exec mysql mysql -u app_user -papp_password -e "SHOW DATABASES;"
```

## 定时任务

### Crontab 配置格式

```bash
SCHEDULE_CRONTAB=分 时 日 月 周
```

| 字段 | 取值范围 | 说明 |
|-----|---------|------|
| 分 | 0-59 | 分钟 |
| 时 | 0-23 | 小时 |
| 日 | 1-31 | 日期 |
| 月 | 1-12 | 月份 |
| 周 | 0-7 | 星期（0 和 7 都表示周日） |

### 常用配置示例

```bash
# 每天 8:00
SCHEDULE_CRONTAB=0 8 * * *

# 每天 6:30
SCHEDULE_CRONTAB=30 6 * * *

# 每周一 9:00
SCHEDULE_CRONTAB=0 9 * * 1

# 每月1号 10:00
SCHEDULE_CRONTAB=0 10 1 * *

# 每 6 小时（0点, 6点, 12点, 18点）
SCHEDULE_CRONTAB=0 */6 * * *

# 工作日（周一到周五）9:00
SCHEDULE_CRONTAB=0 9 * * 1-5

# 禁用定时任务
SCHEDULE_CRONTAB=
```

### 重启定时任务

修改配置后需要重启 Celery Beat：

```bash
# Docker 环境
docker-compose restart celery_beat

# 本地环境
# 先按 Ctrl+C 停止，然后重新运行
python run_beat.py
```

## 扩展开发

### 切换 AI 模型

系统使用标准的 OpenAI API 格式，切换不同的 AI 提供商非常简单：

```bash
# 1. 打开 .env 文件
# 2. 修改以下三个配置项

AI_API_KEY=your-new-api-key
AI_BASE_URL=https://your-provider-api-url/v1
AI_MODEL=your-model-name

# 3. 保存文件，下次调用时自动使用新配置
```

**常见 AI 提供商配置：**

```bash
# OpenAI
AI_API_KEY=sk-xxx
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-3.5-turbo

# 智谱AI
AI_API_KEY=xxx.xxx
AI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
AI_MODEL=glm-4.7

# DeepSeek
AI_API_KEY=sk-xxx
AI_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat

# 通义千问
AI_API_KEY=sk-xxx
AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL=qwen-turbo
```

### 添加新的消息源

#### 1. 创建适配器

在 `adapters/` 目录下创建新文件：

```python
# adapters/my_source_adapter.py
from adapters.base import BaseAdapter
from core.models import Article, SourceType

class MySourceAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(source_type=SourceType.CUSTOM)

    async def fetch_article_list(self, limit: int = 10) -> list[str]:
        """获取文章 URL 列表"""
        # 实现你的逻辑
        return ["url1", "url2"]

    async def fetch_article(self, url: str) -> Article | None:
        """获取单篇文章内容"""
        # 实现你的逻辑
        return Article(
            title="文章标题",
            content="文章内容",
            source_url=url,
            source_type=SourceType.CUSTOM
        )

    async def validate_url(self, url: str) -> bool:
        """验证 URL 是否有效"""
        # 实现你的逻辑
        return True
```

#### 2. 注册适配器

在 `core/constants.py` 中添加新的消息源类型：

```python
class SourceType(str, Enum):
    AIBASE = "aibase"
    RSS = "rss"
    API = "api"
    CUSTOM = "my_source"  # 新增
```

在 `adapters/factory.py` 中注册：

```python
from adapters.my_source_adapter import MySourceAdapter

AdapterFactory.register_adapter(SourceType.CUSTOM, MySourceAdapter)
```

#### 3. 使用新消息源

```bash
# 命令行
python run_system.py --sources my_source

# API
POST /api/v1/briefing/generate
{"sources": ["my_source"]}
```

## 常见问题

### 1. 如何切换 AI 模型？

**最简单的方法：** 修改 `.env` 文件

```bash
# .env 文件
AI_API_KEY=your-new-api-key
AI_BASE_URL=https://your-provider-url/v1
AI_MODEL=your-model-name
```

下次调用 AI 时会自动使用新配置。

### 2. AI 总结很慢怎么办？

**原因：** AI 请求是串行的，默认并发数为 3。

**解决：** 调整并发数

```bash
# .env 文件
AI_SUMMARY_CONCURRENT=10  # 增加到 10 个并发
```

### 3. AI API 调用失败怎么办？

**常见原因：**
1. API 密钥错误或过期
2. API 地址配置错误
3. 网络连接问题
4. 余额不足

**排查步骤：**

```bash
# 1. 检查配置
python -c "from config.settings import get_ai_settings; print(get_ai_settings())"

# 2. 测试 API 连接
python -c "
from services.ai_summary_service import AISummaryService
from config.settings import get_ai_settings
key, url, model = get_ai_settings()
service = AISummaryService(api_key=key, base_url=url, model=model)
print('AI service initialized:', service.client.base_url)
"
```

### 4. 如何禁止定时任务？

**解决：** 留空 crontab 配置

```bash
# .env 文件
SCHEDULE_CRONTAB=
```

### 5. Redis 连接失败怎么办？

**检查：**
1. Redis 服务是否启动
2. 主机地址和端口是否正确
3. 密码是否配置正确

**解决：**

```bash
# 本地 Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# 远程 Redis
REDIS_HOST=your_redis_host
REDIS_PASSWORD=your_password
```

### 6. 数据库连接失败怎么办？

**检查：**
1. 数据库服务是否启动
2. 连接字符串格式是否正确
3. 用户权限是否足够

**解决：**

```bash
# 正确的连接字符串格式
DATABASE_URL=mysql+pymysql://用户名:密码@主机:端口/数据库名
```

### 6. 如何生成 API 密钥？

```bash
python scripts/generate_api_key.py
```

输出：
```
Generated API Key:
  MBjQ3pv1ZsFxJo83Pn93SCA1E31or7Np

Usage:
  1. Copy the key above
  2. Paste it to .env file: API_KEY=MBjQ3pv1ZsFxJo83Pn93SCA1E31or7Np
  3. Restart API server
```

### 7. Docker 启动失败怎么办？

**检查日志：**

```bash
docker-compose logs web
docker-compose logs celery_worker
docker-compose logs celery_beat
```

**常见原因：**
1. 环境变量未配置
2. 端口被占用
3. 数据库连接失败

**解决：**

```bash
# 检查端口占用
netstat -ano | findstr :8080

# 检查环境变量
docker-compose config

# 重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 8. Celery Beat 报错 `TypeError: 'property' object is not iterable`

**原因：** `celery_config.py` 中的 `beat_schedule` 配置错误。

**解决：** 确保使用正确的配置方式

```python
# config/celery_config.py
def get_beat_schedule():
    return {
        'task-name': {
            'task': 'tasks.daily_generation.generate_daily_briefing_task',
            'schedule': crontab(minute='0', hour='8'),
        }
    }

# tasks/celery_app.py
from config.celery_config import get_beat_schedule
celery_app.conf.beat_schedule = get_beat_schedule()
```

### 9. 推荐使用哪个 AI 模型？

**根据场景选择：**

| 使用场景 | 推荐模型 | 原因 |
|---------|---------|------|
| **个人学习/测试** | DeepSeek-chat | 价格便宜，质量不错 |
| **商业项目** | 智谱AI GLM-4.7 | 国产稳定，中文友好 |
| **国际化项目** | OpenAI GPT-3.5/4 | 质量最好，生态成熟 |
| **阿里云用户** | 通义千问 Qwen | 与阿里云集成方便 |
| **高并发场景** | DeepSeek-chat | 性价比最高 |

**配置建议：**

```bash
# DeepSeek（推荐：性价比高）
AI_API_KEY=sk-your-deepseek-key
AI_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat

# 智谱AI（推荐：国产稳定）
AI_API_KEY=your-zhipuai-key
AI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
AI_MODEL=glm-4.7
```

## 许可证

[MIT](LICENSE)

Copyright (c) 2025 qfgk

---

## 联系方式

- GitHub: [qfgk](https://github.com/qfgk)
- 项目地址: [https://github.com/qfgk/ai_morning_news](https://github.com/qfgk/ai_morning_news)
