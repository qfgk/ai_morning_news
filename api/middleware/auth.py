"""
API 认证中间件
"""
from flask import request, jsonify
from functools import wraps
from config.settings import get_settings


def require_api_key(f):
    """API密钥验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        settings = get_settings()

        # 如果未设置API密钥，跳过验证（开发环境）
        if not settings.API_KEY:
            return f(*args, **kwargs)

        # 从请求头获取API密钥
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return jsonify({
                "code": 401,
                "message": "缺少API密钥，请在请求头中添加 X-API-Key"
            }), 401

        if api_key != settings.API_KEY:
            return jsonify({
                "code": 403,
                "message": "API密钥无效"
            }), 403

        return f(*args, **kwargs)

    return decorated_function


def check_api_key_optional(f):
    """可选的API密钥验证（部分接口允许无密钥访问但限流）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        settings = get_settings()

        # 从请求头获取API密钥
        api_key = request.headers.get('X-API-Key')

        # 如果有密钥，验证它
        if api_key and settings.API_KEY:
            if api_key != settings.API_KEY:
                return jsonify({
                    "code": 403,
                    "message": "API密钥无效"
                }), 403

        # 无密钥时的处理（可以添加限流逻辑）
        if not api_key and settings.API_KEY:
            # 可以记录日志或限流
            pass

        return f(*args, **kwargs)

    return decorated_function
