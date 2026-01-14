"""
通用 Webhook 推送服务（支持多个推送地址）
"""
import logging
import requests
from typing import Optional, Dict, Any, List
from config.settings import get_settings

logger = logging.getLogger(__name__)


class WebhookService:
    """通用 Webhook 推送服务（支持多地址推送）"""

    def __init__(self, webhook_urls: Optional[str] = None):
        """
        初始化 Webhook 推送服务

        Args:
            webhook_urls: 接收端 URL（多个用逗号或分号分隔，从环境变量读取）
        """
        settings = get_settings()
        urls = webhook_urls or settings.WEBHOOK_URL

        # 支持多种分隔符：逗号、分号、空格
        if urls:
            import re
            # 使用逗号、分号或空格分隔
            self.webhook_urls = re.split(r'[,;\s]+', urls.strip())
            # 过滤空字符串
            self.webhook_urls = [url.strip() for url in self.webhook_urls if url.strip()]
        else:
            self.webhook_urls = []

        self.timeout = 10

        logger.info(f"初始化 Webhook 服务，共 {len(self.webhook_urls)} 个推送地址")

    def send(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """
        发送数据到所有 Webhook URL

        Args:
            data: 要发送的数据（字典格式）

        Returns:
            每个 URL 的推送结果 {url: success}
        """
        if not self.webhook_urls:
            logger.warning("WEBHOOK_URL 未配置，跳过推送")
            return {}

        results = {}

        for url in self.webhook_urls:
            try:
                logger.info(f"正在推送到: {url}")
                response = requests.post(
                    url,
                    json=data,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )

                success = response.status_code == 200
                results[url] = success

                if success:
                    logger.info(f"✅ 推送成功: {url}")
                else:
                    logger.error(f"❌ 推送失败: {url} - {response.status_code} - {response.text}")

            except requests.exceptions.Timeout:
                logger.error(f"❌ 推送超时: {url}")
                results[url] = False
            except Exception as e:
                logger.error(f"❌ 推送异常: {url} - {e}")
                results[url] = False

        # 汇总结果
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        logger.info(f"推送完成: {success_count}/{total_count} 成功")

        return results

    def send_briefing(self, briefing_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        发送早报数据（标准格式）

        Args:
            briefing_data: 早报数据

        Returns:
            每个URL的推送结果 {url: success}
        """
        # 构建标准推送格式
        payload = {
            "type": "daily_briefing",
            "data": briefing_data
        }

        return self.send(payload)
