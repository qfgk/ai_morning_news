"""
健康检查路由
"""
from flask import Blueprint, jsonify, current_app
import logging

from api.middleware.error_handler import InternalError

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查 - 豁免速率限制"""
    # 从 current_app 获取 limiter 并豁免此路由
    # 注意：实际豁免在请求级别处理，这里仅作说明
    # Flask-Limiter 会在装饰器级别处理豁免

    status = {
        "service": "ok",
        "database": "unknown",
        "redis": "unknown"
    }

    # 检查数据库
    try:
        from database import get_db_manager
        from sqlalchemy import text
        db_manager = get_db_manager()
        with db_manager.get_session() as session:
            session.execute(text("SELECT 1"))
        status["database"] = "ok"
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        status["database"] = "error"

    # 检查Redis
    try:
        import asyncio
        from cache.redis_client import RedisClient
        from config.settings import get_settings

        settings = get_settings()
        redis = RedisClient(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB
        )
        # 在同步上下文中运行异步代码
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(redis.connect())
            loop.run_until_complete(redis.ping())
            status["redis"] = "ok"
        finally:
            loop.run_until_complete(redis.disconnect())
            loop.close()
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        status["redis"] = "error"

    all_ok = all(v == "ok" for v in status.values())
    status_code = 200 if all_ok else 503

    return jsonify(status), status_code


# 豁免健康检查路由的速率限制
health_check.exempt = True
