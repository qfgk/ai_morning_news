"""
错误处理中间件
"""
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """API错误基类"""
    def __init__(self, message: str, code: int = 400, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIError):
    """验证错误"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 400, details)


class NotFoundError(APIError):
    """资源未找到错误"""
    def __init__(self, message: str = "资源未找到"):
        super().__init__(message, 404)


class InternalError(APIError):
    """内部服务器错误"""
    def __init__(self, message: str = "内部服务器错误"):
        super().__init__(message, 500)


def register_error_handlers(app):
    """注册错误处理器"""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        """处理API错误"""
        response = {
            "code": error.code,
            "message": error.message,
        }
        if error.details:
            response["details"] = error.details
        return jsonify(response), error.code

    @app.errorhandler(404)
    def handle_not_found(error):
        """处理404错误"""
        return jsonify({
            "code": 404,
            "message": "接口不存在"
        }), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        """处理500错误"""
        logger.error(f"Internal error: {error}")
        return jsonify({
            "code": 500,
            "message": "内部服务器错误"
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        """处理未捕获的异常"""
        logger.exception(f"Unhandled exception: {error}")
        return jsonify({
            "code": 500,
            "message": "服务器错误"
        }), 500
