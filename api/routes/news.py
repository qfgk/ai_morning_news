"""
新闻API路由
"""
from flask import Blueprint, request, jsonify
import asyncio
import logging
from datetime import datetime

from api.middleware.error_handler import NotFoundError, APIError
from api.middleware.auth import require_api_key
from api.schemas.news_schemas import ApiResponse
from services.news_service import NewsService
from services.ai_summary_service import AISummaryService
from repositories.news_repository import NewsRepository
from cache.cache_repository import CacheRepository
from cache.redis_client import RedisClient
from config.settings import get_settings, get_ai_settings
from utils.validation import validate_date_format

logger = logging.getLogger(__name__)

news_bp = Blueprint('news', __name__)

# 全局缓存服务实例（线程本地存储）
import threading
_thread_local = threading.local()


def _get_cache_repo():
    """获取或创建当前线程的缓存仓库"""
    # 检查当前线程是否已有缓存仓库
    if hasattr(_thread_local, 'cache_repo') and _thread_local.cache_repo is not None:
        return _thread_local.cache_repo

    settings = get_settings()
    try:
        redis_client = RedisClient(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB
        )
        # 为当前线程创建事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Loop is closed")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(redis_client.connect())
        if loop.run_until_complete(redis_client.ping()):
            cache_repo = CacheRepository(redis_client)
            _thread_local.cache_repo = cache_repo
            _thread_local.redis_client = redis_client
            logger.info("Redis cache initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize cache repository: {e}")
        _thread_local.cache_repo = None

    return _thread_local.cache_repo


def get_news_service():
    """获取新闻服务实例"""
    settings = get_settings()

    # 获取 AI 配置
    try:
        api_key, base_url, model = get_ai_settings()
    except ValueError as e:
        logger.error(f"AI 配置错误: {e}")
        raise APIError(f"AI 配置错误: {str(e)}", 500)

    ai_service = AISummaryService(
        api_key=api_key,
        base_url=base_url,
        model=model,
        max_concurrent=settings.AI_SUMMARY_CONCURRENT
    )

    news_repo = None
    try:
        news_repo = NewsRepository()
    except Exception as e:
        logger.warning(f"Failed to initialize news repository: {e}")

    # 获取当前线程的缓存仓库
    cache_repo = _get_cache_repo()

    return NewsService(
        ai_service=ai_service,
        news_repo=news_repo,
        cache_repo=cache_repo
    )


@news_bp.route('/briefing/latest', methods=['GET'])
@require_api_key
def get_latest_briefing():
    """获取最新早报"""
    try:
        news_service = get_news_service()

        # 获取或创建当前线程的事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        briefing = loop.run_until_complete(news_service.get_latest_briefing())

        if not briefing:
            return jsonify({
                "code": 200,
                "message": "暂无本日早报数据",
                "data": None
            })

        return jsonify({
            "code": 200,
            "message": "success",
            "data": briefing.to_dict()
        })
    except APIError:
        raise
    except Exception as e:
        logger.exception(f"Error getting latest briefing: {e}")
        raise APIError(f"服务器错误: {str(e)}", 500)


@news_bp.route('/briefing/<date>', methods=['GET'])
@require_api_key
def get_briefing_by_date(date: str):
    """获取指定日期早报"""
    try:
        # 验证日期格式
        if not validate_date_format(date):
            return jsonify({
                "code": 400,
                "message": "日期格式错误，应为 YYYY-MM-DD"
            }), 400

        news_service = get_news_service()

        # 获取或创建当前线程的事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        briefing = loop.run_until_complete(news_service.get_briefing_by_date(date))

        if not briefing:
            return jsonify({
                "code": 200,
                "message": f"暂无 {date} 的早报数据",
                "data": None
            })

        return jsonify({
            "code": 200,
            "message": "success",
            "data": briefing.to_dict()
        })
    except APIError:
        raise
    except Exception as e:
        logger.exception(f"Error getting briefing by date: {e}")
        raise APIError(f"服务器错误: {str(e)}", 500)


@news_bp.route('/briefing/generate', methods=['POST'])
@require_api_key
def generate_briefing():
    """手动生成早报"""
    try:
        data = request.get_json() or {}

        date = data.get('date') or datetime.now().strftime("%Y-%m-%d")
        sources = data.get('sources', ['aibase'])
        limit = data.get('limit', 10)
        use_cache = data.get('use_cache', True)
        save_to_db = data.get('save_to_db', False)

        # 验证日期格式
        if date and not validate_date_format(date):
            return jsonify({
                "code": 400,
                "message": "日期格式错误，应为 YYYY-MM-DD"
            }), 400

        news_service = get_news_service()

        # 获取或创建当前线程的事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        briefing = loop.run_until_complete(
            news_service.generate_daily_briefing(
                date=date,
                sources=sources,
                limit=limit,
                use_cache=use_cache,
                save_to_db=save_to_db
            )
        )

        return jsonify({
            "code": 200,
            "message": "早报生成成功",
            "data": briefing.to_dict()
        })
    except APIError:
        raise
    except Exception as e:
        logger.exception(f"Error generating briefing: {e}")
        raise APIError(f"生成失败: {str(e)}", 500)


@news_bp.route('/briefing/list', methods=['GET'])
@require_api_key
def list_briefings():
    """分页查询早报列表"""
    try:
        news_repo = NewsRepository()
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)

        # 限制范围
        limit = min(max(1, limit), 100)

        briefings = news_repo.list_briefings(limit=limit, offset=offset)

        return jsonify({
            "code": 200,
            "message": "success",
            "data": {
                "briefings": briefings,
                "count": len(briefings),
                "limit": limit,
                "offset": offset
            }
        })
    except Exception as e:
        logger.exception(f"Error listing briefings: {e}")
        raise APIError(f"服务器错误: {str(e)}", 500)
