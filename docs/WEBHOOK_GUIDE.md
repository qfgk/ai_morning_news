# Webhook 推送功能使用指南

## 功能说明

早报生成系统支持在生成早报后，自动推送到多个 Webhook URL。你可以：
- 推送到企业微信机器人
- 推送到钉钉机器人
- 推送到飞书机器人
- 推送到自己的服务器
- 同时推送到多个地址

## 配置方法

### 1. 环境变量配置

在 `.env` 文件中添加：

```bash
# 单个推送地址
WEBHOOK_URL=https://your-server.com/webhook

# 多个推送地址（用逗号、分号或空格分隔）
WEBHOOK_URL=https://server1.com/webhook,https://server2.com/api/push

# 是否启用推送
WEBHOOK_ENABLED=True
```

### 2. 推送数据格式

系统会向配置的 URL 发送 POST 请求，Content-Type 为 `application/json`：

```json
{
  "type": "daily_briefing",
  "data": {
    "date": "2026-01-14",
    "title": "早报标题",
    "summary": "今日科技新闻摘要...",
    "total_count": 10,
    "articles": [
      {
        "title": "文章标题",
        "summary": "文章摘要...",
        "source_url": "https://example.com/article",
        "source_type": "aibase",
        "publication_date": "2026-01-14"
      }
    ]
  }
}
```

## 接收端开发

### 示例 1: Flask 接收端

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/briefing', methods=['POST'])
def receive_briefing():
    data = request.json

    # 验证数据类型
    if data.get('type') != 'daily_briefing':
        return jsonify({'error': 'Invalid type'}), 400

    briefing_data = data.get('data', {})

    # 提取数据
    title = briefing_data.get('title')
    articles = briefing_data.get('articles', [])

    # TODO: 处理推送逻辑
    print(f"收到早报: {title}")

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 示例 2: 推送到企业微信

```python
import requests

def send_to_wechat(webhook_url, briefing_data):
    title = briefing_data.get('title')
    articles = briefing_data.get('articles', [])

    # 构建 Markdown
    content = f"# {title}\n\n"
    for idx, article in enumerate(articles[:10], 1):
        content += f"{idx}. {article.get('title')}\n"

    # 发送
    data = {
        "msgtype": "markdown",
        "markdown": {"content": content}
    }

    requests.post(webhook_url, json=data)
```

完整示例代码见：`examples/webhook_receiver_examples.py`

## 测试推送

### 方法 1: 手动触发测试

```bash
# 手动触发生成早报
curl -X POST http://localhost:8080/api/v1/briefing/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json"
```

### 方法 2: 使用 Webhook 测试工具

可以使用 [Webhook.site](https://webhook.site) 或 [RequestBin](https://requestbin.com) 创建临时测试 URL。

## 注意事项

1. **网络连通性**: 确保服务器能访问你的 Webhook URL
2. **超时设置**: 默认超时 10 秒，超时会记录错误但不会中断任务
3. **失败重试**: 目前不支持自动重试，建议在接收端做好幂等处理
4. **数据安全**: Webhook URL 建议使用 HTTPS，并添加认证机制

## 日志查看

```bash
# Docker 环境
docker logs ainews_celery_worker | grep "Webhook"

# 本地环境
# 查看日志输出
```

## 常见问题

### Q: 推送失败会影响早报生成吗？
A: 不会。推送失败只记录日志，不影响主任务。

### Q: 如何确认推送成功？
A: 查看 Worker 日志，会显示 "Webhook 推送完成: X/Y 成功"。

### Q: 支持推送文件吗？
A: 目前只支持 JSON 数据，不支持文件上传。

### Q: 如何调试推送问题？
A:
1. 使用 webhook.site 等工具测试
2. 查看容器日志
3. 在接收端打印日志
