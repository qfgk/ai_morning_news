"""
数据验证工具
"""
import re
from datetime import datetime
from typing import Optional


def validate_date_format(date_str: str) -> bool:
    """验证日期格式 YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_url(url: str) -> bool:
    """验证URL格式"""
    url_pattern = re.compile(
        r'^https?://'  # http or https
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
        r'(?::\d+)?'  # port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    return email_pattern.match(email) is not None


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """清理输入文本"""
    if not text:
        return ""

    # 去除首尾空格
    text = text.strip()

    # 限制长度
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text
