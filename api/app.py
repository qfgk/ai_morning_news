"""
Flask 应用工厂
"""
from flask import Flask
from config.settings import get_settings


def create_app(config_name: str = None) -> Flask:
    """创建Flask应用"""
    app = Flask(__name__)

    # 加载配置
    settings = get_settings()
    app.config['DEBUG'] = settings.DEBUG
    app.config['ENVIRONMENT'] = settings.ENVIRONMENT

    # 注册蓝图
    from api.routes.news import news_bp
    from api.routes.health import health_bp

    app.register_blueprint(news_bp, url_prefix='/api/v1')
    app.register_blueprint(health_bp)

    # 注册错误处理
    from api.middleware.error_handler import register_error_handlers
    register_error_handlers(app)

    return app


def create_app_async():
    """创建异步应用（可选）"""
    # 未来可以扩展为使用Quart等异步框架
    return create_app()
