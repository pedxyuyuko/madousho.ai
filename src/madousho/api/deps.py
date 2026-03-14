"""依赖注入模块 - 数据库会话依赖项"""

from typing import Generator

from sqlalchemy.orm import Session

from madousho.database.connection import Database


def get_db() -> Generator[Session, None, None]:
    """依赖注入：数据库 Session

    Yields:
        Session: SQLAlchemy 数据库会话
    """
    db = Database.get_instance()
    with db.session() as session:
        yield session
