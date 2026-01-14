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
from config.settings import get_settings, get_ai_settings

logger = logging.getLogger(__name__)


async def _generate_briefing_async(date: str, settings, ai_service, news_repo):
    """异步生成早报的辅助函数"""
    cache_repo = None
    redis_client = None

    try:
        # 连接 Redis
        redis_client = RedisClient(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB
        )
        await redis_client.connect()
        if await redis_client.ping():
            cache_repo = CacheRepository(redis_client)
            logger.info("Redis连接成功")

        # 获取任务锁
        if cache_repo:
            lock_acquired = await cache_repo.acquire_task_lock("daily_briefing", date)
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

            briefing = await news_service.generate_daily_briefing(
                date=date,
                sources=["aibase"],
                limit=settings.CRAWLER_MAX_ARTICLES,
                use_cache=True,
                save_to_db=True
            )

            logger.info(f"早报生成成功: {briefing.title}, 共 {briefing.total_count} 篇文章")

            return {
                "status": "success",
                "date": date,
                "total_count": briefing.total_count,
                "briefing": briefing
            }

        finally:
            # 释放任务锁
            if cache_repo:
                await cache_repo.release_task_lock("daily_briefing", date)

    finally:
        # 关闭Redis连接
        if redis_client:
            await redis_client.disconnect()


@celery_app.task(name='tasks.daily_generation.generate_daily_briefing_task')
def generate_daily_briefing_task():
    """每日早报生成任务"""
    date = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"开始生成 {date} 的早报...")

    start_time = datetime.now()
    settings = get_settings()

    try:
        # 初始化 AI 服务
        try:
            api_key, base_url, model = get_ai_settings()
        except ValueError as e:
            logger.error(f"AI 配置错误: {e}")
            return {
                "status": "failed",
                "date": date,
                "error": str(e),
                "duration": 0
            }

        ai_service = AISummaryService(
            api_key=api_key,
            base_url=base_url,
            model=model,
            max_concurrent=settings.AI_SUMMARY_CONCURRENT
        )

        # 初始化数据库
        news_repo = None
        try:
            news_repo = NewsRepository()
            logger.info("数据库连接成功")
        except Exception as e:
            logger.warning(f"数据库连接失败: {e}")

        # 运行异步任务（只创建一次事件循环）
        result = asyncio.run(_generate_briefing_async(date, settings, ai_service, news_repo))

        # 计算耗时
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds())

        # 记录任务日志
        if result.get("status") == "success":
            if news_repo:
                news_repo.log_task(
                    task_name="daily_briefing",
                    status="success",
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    result=f"生成 {result['total_count']} 篇文章"
                )

            # Webhook 推送
            if settings.WEBHOOK_ENABLED:
                try:
                    from services.webhook_service import WebhookService
                    webhook = WebhookService()

                    # 构建推送数据
                    briefing_dict = result["briefing"].to_dict() if hasattr(result.get("briefing"), "to_dict") else result.get("briefing", {})

                    # 推送
                    push_results = webhook.send_briefing(briefing_dict)

                    # 记录推送结果
                    success_count = sum(1 for v in push_results.values() if v)
                    logger.info(f"Webhook 推送完成: {success_count}/{len(push_results)} 成功")
                except Exception as e:
                    logger.warning(f"Webhook 推送失败: {e}")

            return {
                "status": "success",
                "date": date,
                "total_count": result["total_count"],
                "duration": duration
            }
        else:
            return result

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
