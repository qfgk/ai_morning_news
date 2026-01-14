"""
Webhook 接收端示例代码

本文件展示如何创建接收早报推送的服务端
"""

# ============================================================================
# 示例 1: Flask 接收端（推荐用于简单场景）
# ============================================================================

from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/webhook/briefing', methods=['POST'])
def receive_briefing():
    """接收早报推送"""
    try:
        data = request.json

        # 验证数据类型
        if data.get('type') != 'daily_briefing':
            return jsonify({'error': 'Invalid type'}), 400

        briefing_data = data.get('data', {})

        # 提取关键信息
        title = briefing_data.get('title', '早报')
        date = briefing_data.get('date', '')
        summary = briefing_data.get('summary', '')
        articles = briefing_data.get('articles', [])

        logger.info(f"收到早报: {title} ({date})")
        logger.info(f"共 {len(articles)} 篇文章")

        # TODO: 在这里处理推送逻辑
        # - 发送到微信机器人
        # - 发送到钉钉机器人
        # - 发送到邮件
        # - 存储到数据库

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"处理失败: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


# ============================================================================
# 示例 2: FastAPI 接收端（推荐用于高性能场景）
# ============================================================================

"""
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()


@app.post("/webhook/briefing")
async def receive_briefing(request: Request):
    '''接收早报推送'''
    data = await request.json()

    if data.get('type') != 'daily_briefing':
        return {'error': 'Invalid type'}

    briefing_data = data.get('data', {})

    # 处理早报数据
    print(f"收到早报: {briefing_data.get('title')}")

    # TODO: 处理推送逻辑

    return {'status': 'success'}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
"""


# ============================================================================
# 示例 3: 推送到企业微信机器人
# ============================================================================

"""
import requests

def send_to_wechat_webhook(webhook_url: str, briefing_data: dict):
    '''推送到企业微信机器人'''

    # 构建消息内容
    title = briefing_data.get('title', '早报')
    date = briefing_data.get('date', '')
    summary = briefing_data.get('summary', '')
    articles = briefing_data.get('articles', [])

    # 构建 Markdown 消息
    content = f"# {title}\n\n"
    content += f"**日期**: {date}\n\n"
    content += f"**摘要**: {summary}\n\n"

    for idx, article in enumerate(articles[:10], 1):
        content += f"{idx}. {article.get('title', '无标题')}\n"

    # 发送到企业微信
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }

    response = requests.post(webhook_url, json=data)
    return response.json()


# 使用示例
# webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
# send_to_wechat_webhook(webhook_url, briefing_data)
"""


# ============================================================================
# 示例 4: 推送到钉钉机器人
# ============================================================================

"""
import requests

def send_to_dingtalk_webhook(webhook_url: str, briefing_data: dict):
    '''推送到钉钉机器人'''

    title = briefing_data.get('title', '早报')
    articles = briefing_data.get('articles', [])

    # 构建 Markdown 消息
    text = f"## {title}\n\n"
    for idx, article in enumerate(articles[:10], 1):
        text += f"### {idx}. {article.get('title', '无标题')}\n\n"
        if article.get('summary'):
            text += f"{article['summary'][:100]}...\n\n"

    # 发送到钉钉
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": text
        }
    }

    response = requests.post(webhook_url, json=data)
    return response.json()


# 使用示例
# webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
# send_to_dingtalk_webhook(webhook_url, briefing_data)
"""


# ============================================================================
# 示例 5: 推送到飞书机器人
# ============================================================================

"""
import requests

def send_to_feishu_webhook(webhook_url: str, briefing_data: dict):
    '''推送到飞书机器人'''

    title = briefing_data.get('title', '早报')
    articles = briefing_data.get('articles', [])

    # 构建卡片消息
    card_content = []

    for article in articles[:10]:
        card_content.append({
            "tag": "div",
            "text": {
                "content": f"**{article.get('title', '无标题')}**\n{article.get('summary', '')[:100]}...",
                "tag": "lark_md"
            }
        })

    data = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "content": title,
                    "tag": "plain_text"
                }
            },
            "elements": card_content
        }
    }

    response = requests.post(webhook_url, json=data)
    return response.json()


# 使用示例
# webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_HOOK_ID"
# send_to_feishu_webhook(webhook_url, briefing_data)
"""


# ============================================================================
# 数据格式说明
# ============================================================================

"""
接收到的 JSON 数据格式：

{
    "type": "daily_briefing",  # 消息类型
    "data": {
        "date": "2026-01-14",           # 日期
        "title": "早报标题",              # 标题
        "summary": "今日摘要...",         # 总体摘要
        "total_count": 10,              # 文章总数
        "articles": [                   # 文章列表
            {
                "title": "文章标题",
                "summary": "文章摘要",
                "source_url": "https://...",
                "source_type": "aibase",
                "publication_date": "2026-01-14"
            },
            // ... 更多文章
        ]
    }
}
"""
