# 早报系统

基于 Python 的智能早报生成系统，支持多消息源、AI 总结、Redis 缓存和定时任务。

## 功能特性

- **多消息源支持**：适配器模式，支持 AIbase、RSS、API 等多种消息源
- **AI 智能总结**：集成智谱 AI，自动生成文章摘要和每日汇总
- **Redis 缓存**：高性能缓存，提升响应速度
- **数据持久化**：MySQL/PostgreSQL 存储早报数据
- **Web API**：RESTful API，方便集成
- **定时任务**：Celery 自动生成每日早报

## 技术栈

| 类别 | 技术 |
|------|------|
| Web框架 | Flask 3.0+ |
| 异步爬虫 | crawl4ai, asyncio |
| 数据库 | MySQL 8.0+ / PostgreSQL 14+ |
| ORM | SQLAlchemy 2.0 |
| 缓存 | Redis 7.0+ |
| 任务队列 | Celery 5.3+ |
| AI | 智谱 AI (GLM-4.7) |

## 项目结构

```
PythonProject/
├── api/                   # Flask Web API
│   ├── app.py            # 应用工厂
│   ├── routes/           # 路由
│   ├── schemas/          # 数据模式
│   └── middleware/       # 中间件
│
├── adapters/             # 消息源适配器
│   ├── base.py           # 抽象基类
│   ├── aibase_adapter.py # AIbase适配器
│   └── factory.py        # 适配器工厂
│
├── cache/                # 缓存层
│   ├── redis_client.py   # Redis客户端
│   ├── cache_keys.py     # 缓存键定义
│   └── cache_repository.py
│
├── config/               # 配置管理
│   ├── settings.py       # 主配置
│   └── celery_config.py  # Celery配置
│
├── core/                 # 核心模块
│   ├── models.py         # 数据模型
│   └── constants.py      # 常量定义
│
├── database/             # 数据库
│   ├── base.py           # 连接管理
│   └── models.py         # SQLAlchemy模型
│
├── repositories/         # 数据访问层
│   └── news_repository.py
│
├── services/             # 业务服务层
│   ├── ai_summary_service.py
│   └── news_service.py
│
├── tasks/                # 后台任务
│   ├── celery_app.py
│   └── daily_generation.py
│
├── scripts/              # 脚本工具
│   ├── init_db.py        # 初始化数据库
│   └── migrate_articles.py
│
├── utils/                # 工具函数
│   └── validation.py
│
├── run_system.py         # 运行早报系统
├── run_api.py            # 启动API服务
├── run_celery.py         # 启动Celery Worker
└── run_beat.py           # 启动Celery Beat
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
copy .env.example .env

# 编辑 .env 文件，配置以下必要项：
# ZHIPUAI_API_KEY=你的智谱AI密钥
# DATABASE_URL=mysql+pymysql://root:password@localhost/morning_news
```

### 3. 初始化数据库（可选）

```bash
python scripts/init_db.py
```

### 4. 运行系统

#### 方式一：直接生成早报

```bash
# 基础模式（仅爬虫+AI）
python run_system.py

# 带数据库
python run_system.py --db

# 带Redis缓存
python run_system.py --redis

# 完整模式（数据库+Redis）
python run_system.py --db --redis
```

c

```bash
python run_api.py
```

API 端点：
- `GET /health` - 健康检查
- `GET /api/v1/briefing/latest` - 获取最新早报
- `GET /api/v1/briefing/<date>` - 获取指定日期早报
- `POST /api/v1/briefing/generate` - 手动生成早报
- `GET /api/v1/briefing/list` - 早报列表

#### 方式三：启动定时任务

```bash
# 终端1：启动Celery Worker
python run_celery.py

# 终端2：启动Celery Beat（定时调度器）
python run_beat.py
```

## API 使用说明

### 安全认证

所有 API 接口（除健康检查外）都需要 API 密钥验证。

#### 1. 生成 API 密钥

```bash
python scripts/generate_api_key.py
```

输出示例：
```
============================================================
API Key Generator
============================================================

Generated API Key:
  MBjQ3pv1ZsFxJo83Pn93SCA1E31or7Np

Usage:
  1. Copy the key above
  2. Paste it to .env file: API_KEY=MBjQ3pv1ZsFxJo83Pn93SCA1E31or7Np
  3. Restart API server
```

#### 2. 配置密钥

在 `.env` 文件中设置：

```bash
API_KEY=MBjQ3pv1ZsFxJo83Pn93SCA1E31or7Np
```

#### 3. API 调用示例

**curl**

```bash
curl -H "X-API-Key: MBjQ3pv1ZsFxJo83Pn93SCA1E31or7Np" \
  http://localhost:5000/api/v1/briefing/latest
```

**Python requests**

```python
import requests

headers = {
    "X-API-Key": "MBjQ3pv1ZsFxJo83Pn93SCA1E31or7Np"
}

response = requests.get(
    "http://localhost:5000/api/v1/briefing/latest",
    headers=headers
)
print(response.json())
```

**JavaScript fetch**

```javascript
fetch('http://localhost:5000/api/v1/briefing/latest', {
    headers: {
        'X-API-Key': 'MBjQ3pv1ZsFxJo83Pn93SCA1E31or7Np'
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

#### 4. 错误响应

**缺少密钥 (401)**
```json
{
    "code": 401,
    "message": "缺少API密钥，请在请求头中添加 X-API-Key"
}
```

**密钥无效 (403)**
```json
{
    "code": 403,
    "message": "API密钥无效"
}
```

#### 5. 接口认证状态

| 接口 | 需要认证 |
|------|---------|
| `GET /health` | ❌ 不需要 |
| `GET /api/v1/briefing/latest` | ✅ 需要 |
| `GET /api/v1/briefing/<date>` | ✅ 需要 |
| `POST /api/v1/briefing/generate` | ✅ 需要 |
| `GET /api/v1/briefing/list` | ✅ 需要 |

#### 6. 安全建议

- ✅ 定期更换 API 密钥
- ✅ 生产环境使用 HTTPS
- ✅ 不要在客户端代码中暴露密钥
- ✅ 为不同客户端使用不同密钥
- ✅ 监控异常请求

### API 接口说明

#### 获取最新早报

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/api/v1/briefing/latest
```

#### 获取指定日期早报

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/api/v1/briefing/2025-01-13
```

#### 手动生成早报

```bash
curl -X POST http://localhost:5000/api/v1/briefing/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-01-13",
    "sources": ["aibase"],
    "limit": 10,
    "save_to_db": true
  }'
```

#### 早报列表

```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:5000/api/v1/briefing/list?limit=10&offset=0"
```

### 响应格式

成功响应：
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "date": "2025-01-13",
        "title": "早报 - 2025-01-13",
        "articles": [...],
        "total_count": 10,
        "ai_summary": "今日要闻..."
    }
}
```

## Docker 部署

### 1. 准备环境变量

```bash
# 复制 Docker 环境变量模板
copy .env.docker.example .env

# 编辑 .env 文件，配置必要参数
# ZHIPUAI_API_KEY=你的智谱AI密钥
# API_KEY=生成的API密钥
```

### 2. 启动所有服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f web
```

### 3. 服务说明

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| Web API | morning_news_web | 5000 | API服务 |
| MySQL | morning_news_db | 3306 | 数据库 |
| Redis | morning_news_redis | 6379 | 缓存 |
| Celery Worker | morning_news_celery_worker | - | 任务执行 |
| Celery Beat | morning_news_celery_beat | - | 定时调度 |

### 4. 常用命令

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重启服务
docker-compose restart

# 进入容器
docker-compose exec web bash

# 初始化数据库
docker-compose exec web python scripts/init_db.py

# 手动生成早报
docker-compose exec web python run_system.py --db

# 查看实时日志
docker-compose logs -f --tail=100 web celery_worker celery_beat
```

### 5. 健康检查

```bash
# 检查服务健康状态
curl http://localhost:5000/health

# 检查数据库连接
docker-compose exec mysql mysql -u app_user -papp_password -e "SHOW DATABASES;"
```

### 6. 数据备份

```bash
# 备份MySQL数据
docker-compose exec mysql mysqldump -u root -proot_password morning_news > backup.sql

# 恢复MySQL数据
docker-compose exec -T mysql mysql -u root -proot_password morning_news < backup.sql

# 备份Redis数据
docker-compose exec redis redis-cli --rdb /data/dump.rdb

# 备份整个数据卷
docker run --rm -v morning_news_mysql_data:/data -v $(pwd):/backup alpine tar czf /backup/mysql_backup.tar.gz -C /data .
```

### 7. 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose down
docker-compose up -d
```

## 扩展消息源

在 `adapters/` 目录下创建新的适配器：

```python
# adapters/my_adapter.py
from adapters.base import BaseAdapter
from core.models import Article, SourceType

class MyAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(source_type=SourceType.CUSTOM)

    async def fetch_article_list(self, limit: int = 10):
        # 实现获取文章列表逻辑
        pass

    async def fetch_article(self, url: str):
        # 实现获取单篇文章逻辑
        pass

    async def validate_url(self, url: str):
        # 实现URL验证逻辑
        pass
```

然后在 `adapters/factory.py` 中注册：

```python
from adapters.my_adapter import MyAdapter

AdapterFactory.register_adapter(SourceType.CUSTOM, MyAdapter)
```

## 许可证

MIT
