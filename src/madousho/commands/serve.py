"""Serve command for Madousho.ai API server."""

import os
import sys

import typer
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command
from pydantic import ValidationError

from madousho.config.loader import init_config, get_config_file
from madousho.database.connection import Database
from madousho.config.loader import get_config
from madousho.logging.config import configure_logging
from loguru import logger

app = typer.Typer()


def ensure_database_directory(database_url: str) -> None:
    """确保数据库文件所在目录存在"""
    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Database directory created: {db_dir}")


def run_alembic_migrations(database_url: str) -> None:
    """运行 Alembic 迁移到最新版本"""
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    alembic_command.upgrade(alembic_cfg, "head")
    logger.info("Alembic migrations completed")


def init_database() -> None:
    """初始化数据库连接、运行迁移、验证连接"""
    try:
        config = get_config()
    except ValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        sys.exit(2)
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        sys.exit(2)

    # 确保数据库目录存在
    ensure_database_directory(config.database.url)

    # 初始化数据库连接
    db = Database.get_instance()
    db.init(
        database_url=config.database.url,
        sqlite_config=config.database.sqlite.model_dump(),
    )
    logger.info(f"Database connection initialized: {config.database.url}")

    # 运行 Alembic 迁移
    run_alembic_migrations(config.database.url)

    # 连接测试
    try:
        with db.session() as session:
            _ = session.execute(text("SELECT 1"))
        logger.info("Database connection test passed")
    except OperationalError as e:
        logger.error(f"Database connection test failed: {e}")
        sys.exit(1)
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        sys.exit(1)

    logger.info("Database initialization completed successfully")


@app.command()
def serve(ctx: typer.Context):
    """Madousho.ai API server."""
    verbose = ctx.obj.get("verbose", False)
    json_output = ctx.obj.get("json_output", False)
    config_path = os.environ.get("MADOUSHO_CONFIG_PATH")

    # Initialize logging with global options
    configure_logging(level="DEBUG" if verbose else None, is_json=json_output)

    # Set MADOUSHO_CONFIG_PATH environment variable if config_path is provided
    if config_path is not None:
        os.environ["MADOUSHO_CONFIG_PATH"] = config_path

    # Get the actual config file path that will be used
    resolved_config_path = get_config_file(None)

    # Load configuration
    _ = init_config()

    # Output startup information
    logger.info(f"Configuration loaded from: {resolved_config_path}")

    # Initialize database
    init_database()
