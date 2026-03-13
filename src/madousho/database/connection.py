"""Database singleton class - 一次 init，到处使用"""

from sqlalchemy import create_engine, Engine, event
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Generator, Dict, Any
from contextlib import contextmanager
import logging

from .base_model import Base

logger = logging.getLogger(__name__)


class Database:
    """数据库单例类 - 只负责连接和 Session 管理"""

    _instance: Optional["Database"] = None
    _engine: Optional[Engine] = None
    _session_factory: Optional[scoped_session[Session]] = None
    _sqlite_config: Optional[Dict[str, Any]] = None

    def __new__(cls) -> "Database":
        """单例模式 - 确保只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "Database":
        """获取唯一实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._engine is not None

    def init(self, database_url: str, sqlite_config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化数据库连接

        Args:
            database_url: 数据库 URL, e.g., "sqlite:///./madousho.db"
            sqlite_config: SQLite 配置字典，包含 WAL 和其他性能设置
        """
        if self._engine is not None:
            logger.warning("Database already initialized")
            return

        # 保存配置用于事件监听器
        self._sqlite_config = sqlite_config

        # SQLite 特定配置
        connect_args = {}
        if database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False

        # 从配置中提取池设置
        pool_size = sqlite_config.get("pool_size", 5) if sqlite_config else 5
        pool_timeout = sqlite_config.get("pool_timeout", 30) if sqlite_config else 30
        pool_recycle = sqlite_config.get("pool_recycle", 3600) if sqlite_config else 3600

        self._engine = create_engine(
            database_url,
            connect_args=connect_args,
            echo=False,  # 开发时可设为 True 记录 SQL
            pool_size=pool_size,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
        )

        # 为 SQLite 注册 WAL 配置事件监听器
        if database_url.startswith("sqlite"):
            @event.listens_for(self._engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                """Configure SQLite WAL mode and performance settings on connection."""
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute(f"PRAGMA synchronous={self._sqlite_config.get('synchronous', 'NORMAL') if self._sqlite_config else 'NORMAL'}")
                cursor.execute(f"PRAGMA cache_size={self._sqlite_config.get('cache_size', -64000) if self._sqlite_config else -64000}")
                cursor.execute(f"PRAGMA temp_store={self._sqlite_config.get('temp_store', 'MEMORY') if self._sqlite_config else 'MEMORY'}")
                cursor.execute(f"PRAGMA mmap_size={self._sqlite_config.get('mmap_size', 268435456) if self._sqlite_config else 268435456}")
                cursor.execute(f"PRAGMA journal_size_limit={self._sqlite_config.get('journal_size_limit', 67108864) if self._sqlite_config else 67108864}")
                cursor.execute(f"PRAGMA busy_timeout={self._sqlite_config.get('busy_timeout', 30000) if self._sqlite_config else 30000}")
                if self._sqlite_config.get('foreign_keys', True) if self._sqlite_config else True:
                    cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
                logger.info("SQLite WAL mode enabled")

        self._session_factory = scoped_session(
            sessionmaker(bind=self._engine, autocommit=False, autoflush=False)
        )

        logger.info(f"Database initialized: {database_url}")

    def get_engine(self) -> Engine:
        """获取 SQLAlchemy Engine"""
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call init() first.")
        return self._engine

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Session 上下文管理器 - 自动 commit/rollback

        Usage:
            with db.session() as session:
                # 操作 session
                session.add(obj)
        """
        if self._session_factory is None:
            raise RuntimeError("Database not initialized")
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error: {e}", exc_info=True)
            raise
        finally:
            session.close()

    def create_all_tables(self) -> None:
        """创建所有表结构"""
        if self._engine is None:
            raise RuntimeError("Database not initialized")
        Base.metadata.create_all(self._engine)
        logger.info("All tables created")

    def dispose(self) -> None:
        """关闭数据库连接（用于测试清理）"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Database connection disposed")
