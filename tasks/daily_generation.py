"""
每日早报生成任务
"""
import asyncio
from datetime import datetime
from celery import current_task
import logging

from tasks.celery_app import celery_app
from services.news_service import NewsService
from services.ai_summary_service import AISummaryService
from repositories.news_repository import NewsRepository
from cache.cache_repository import CacheRepository
from cache.redis_client import RedisClient
from config.settings import get_settings

logger = logging.getLogger(__name__)


@celery_app.task(name='tasks.daily_generation.generate_daily_briefing_task')
def generate_daily_briefing_task():
    """每日早报生成任务"""
    date = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"开始生成 {date} 的早报...")

    start_time = datetime.now()
    settings = get_settings()

    try:
        # 初始化服务
        ai_service = AISummaryService(
            api_key=settings.ZHIPUAI_API_KEY,
            base_url=settings.ZHIPUAI_BASE_URL,
            model=settings.ZHIPUAI_MODEL,
            max_concurrent=settings.AI_SUMMARY_CONCURRENT
        )

        news_repo = None
        try:
            news_repo = NewsRepository()
            logger.info("数据库连接成功")
        except Exception as e:
            logger.warning(f"数据库连接失败: {e}")

        cache_repo = None
        redis_client = None
        try:
            redis_client = RedisClient(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB
            )
            # 在Celery任务中需要使用asyncio.run
            asyncio.run(redis_client.connect())
            if asyncio.run(redis_client.ping()):
                cache_repo = CacheRepository(redis_client)
                logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}")

        # 获取任务锁，防止重复执行
        if cache_repo:
            lock_acquired = asyncio.run(cache_repo.acquire_task_lock("daily_briefing", date))
            if not lock_acquired:
                logger.warning(f"任务已在执行中，跳过: {date}")
                return {"status": "skipped", "reason": "lock not acquired"}

        try:
            # 生成早报
            news_service = NewsService(
                ai_service=ai_service,
                news_repo=news_repo,
                cache_repo=cache_repo
            )

            briefing = asyncio.run(
                news_service.generate_daily_briefing(
                    date=date,
                    sources=["aibase"],
                    limit=settings.CRAWLER_MAX_ARTICLES,
                    use_cache=True,
                    save_to_db=True
                )
            )

            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds())

            logger.info(f"早报生成成功: {briefing.title}, 共 {briefing.total_count} 篇文章")

            # 记录任务日志
            if news_repo:
                news_repo.log_task(
                    task_name="daily_briefing",
                    status="success",
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    result=f"生成 {briefing.total_count} 篇文章"
                )

            return {
                "status": "success",
                "date": date,
                "total_count": briefing.total_count,
                "duration": duration
            }

        finally:
            # 释放任务锁
            if cache_repo:
                asyncio.run(cache_repo.release_task_lock("daily_briefing", date))

            # 关闭Redis连接
            if redis_client:
                asyncio.run(redis_client.disconnect())

    except Exception as e:
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds())
        error_msg = str(e)

        logger.error(f"生成早报失败: {error_msg}", exc_info=True)

        # 记录失败日志
        try:
            if news_repo:
                news_repo.log_task(
                    task_name="daily_briefing",
                    status="failed",
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    error_message=error_msg
                )
        except:
            pass

        return {
            "status": "failed",
            "date": date,
            "error": error_msg,
            "duration": duration
        }


@celery_app.task(name='tasks.daily_generation.cleanup_cache_task')
def cleanup_cache_task():
    """清理过期缓存任务"""
    logger.info("开始清理过期缓存...")
    try:
        # 这里可以添加清理逻辑
        # 例如：清理7天前的早报缓存
        logger.info("缓存清理完成")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"缓存清理失败: {e}")
        return {"status": "failed", "error": str(e)}
