"""
Flask 应用工厂
"""
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config.settings import get_settings


# 全局 limiter 实例（稍后初始化）
limiter = None


def create_limiter(settings):
    """根据配置创建速率限制器"""
    global limiter

    if not settings.RATE_LIMIT_ENABLED:
        # 不启用速率限制
        return Limiter(
            key_func=get_remote_address,
            storage_uri="memory://",
            default_limits=[]
        )

    # 构建默认限制
    default_limit = f"{settings.RATE_LIMIT_PER_MINUTE} per minute"

    # 选择存储后端（使用 URI）
    if settings.REDIS_HOST:
        # 使用 Redis 存储（注意：Redis 默认只支持 0-15 号数据库）
        rate_limit_db = min(settings.REDIS_DB + 1, 15)  # 确保不超过15
        if settings.REDIS_PASSWORD:
            storage_uri = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{rate_limit_db}"
        else:
            storage_uri = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{rate_limit_db}"
    else:
        # 使用内存存储
        storage_uri = "memory://"

    return Limiter(
        key_func=get_remote_address,
        storage_uri=storage_uri,
        default_limits=[default_limit],
        strategy="fixed-window"
    )


def create_app(config_name: str = None) -> Flask:
    """创建Flask应用"""
    global limiter

    app = Flask(__name__)

    # 加载配置
    settings = get_settings()
    app.config['DEBUG'] = settings.DEBUG
    app.config['ENVIRONMENT'] = settings.ENVIRONMENT
    # 配置 JSON 输出中文而非 Unicode 转义
    app.json.ensure_ascii = False

    # 创建并初始化速率限制器
    limiter = create_limiter(settings)
    limiter.init_app(app)

    # 将 limiter 保存到 app 配置中，供路由使用
    app.limiter = limiter

    # 注册蓝图
    from api.routes.news import news_bp
    from api.routes.health import health_bp

    app.register_blueprint(news_bp, url_prefix='/api/v1')
    app.register_blueprint(health_bp)

    # 对健康检查路由应用豁免
    health_check = app.view_functions.get('health.health_check')
    if health_check and getattr(health_check, 'exempt', False):
        limiter.exempt(health_check)

    # 注册错误处理
    from api.middleware.error_handler import register_error_handlers
    register_error_handlers(app)

    return app


def create_app_async():
    """创建异步应用（可选）"""
    # 未来可以扩展为使用Quart等异步框架
    return create_app()
