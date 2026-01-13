"""
数据库连接管理
"""
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import get_settings
from database.models import Base


class DBSessionManager:
    """数据库会话管理器"""

    def __init__(self, database_url: Optional[str] = None):
        settings = get_settings()
        self.database_url = database_url or settings.DATABASE_URL

        if not self.database_url:
            raise ValueError("DATABASE_URL 环境变量未设置")

        # 创建引擎
        self.engine = create_engine(
            self.database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # 检查连接有效性
            echo=settings.DEBUG  # 开发环境打印SQL
        )

        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def init_tables(self):
        """初始化数据库表"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """删除所有表（慎用）"""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """获取数据库会话（上下文管理器）"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session_sync(self) -> Session:
        """获取数据库会话（非上下文）"""
        return self.SessionLocal()


# 全局实例
_db_manager: Optional[DBSessionManager] = None


def get_db_manager() -> DBSessionManager:
    """获取数据库管理器单例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DBSessionManager()
    return _db_manager


def init_db():
    """初始化数据库"""
    db_manager = get_db_manager()
    db_manager.init_tables()


def drop_db():
    """删除数据库（慎用）"""
    db_manager = get_db_manager()
    db_manager.drop_tables()


def get_db_session() -> Session:
    """获取数据库会话"""
    db_manager = get_db_manager()
    return db_manager.get_session_sync()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """会话作用域上下文管理器"""
    db_manager = get_db_manager()
    with db_manager.get_session() as session:
        yield session
