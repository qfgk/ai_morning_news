"""
常量定义
"""

# 智谱AI系统提示词
AI_SUMMARY_SYSTEM_PROMPT = """
## Goals
读取并解析 JSON 格式的文章，提炼出文章的主旨，形成最多3句，推荐2句的简洁的概述。

## Constrains:
概述长度不超过 80 字，保持文章的原意和重点。

## Skills
JSON 解析能力，文章内容理解和总结能力。

## Output Format
最多3句，推荐2句概述，简洁明了，不超过 80 字。

## Workflow:
1. 读取并解析 JSON 格式的文章
2. 理解文章内容，提取关键信息
3. 生成简洁的概述，最多3句，推荐2句，不超过 80 字
"""

# AIbase 配置
AIBASE_BASE_URL = "https://www.aibase.com/zh/news/"

# 缓存TTL（秒）
CACHE_TTL_DAILY_BRIEFING = 86400  # 24小时
CACHE_TTL_ARTICLE = 604800  # 7天
CACHE_TTL_LATEST = 900  # 15分钟
CACHE_TTL_TASK_LOCK = 3600  # 1小时
