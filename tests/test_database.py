"""Database module unit tests."""

import pytest
from sqlalchemy import Engine

from madousho.database import Database, BaseModel


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset Database singleton before and after each test."""
    # Reset before test
    Database._instance = None
    Database._engine = None
    Database._session_factory = None
    yield
    # Reset after test
    Database._instance = None
    Database._engine = None
    Database._session_factory = None


@pytest.fixture
def database():
    """Create and setup in-memory SQLite database for testing."""
    db = Database.get_instance()
    db.init("sqlite:///:memory:")
    yield db
    # Cleanup
    db.dispose()


class TestDatabaseSingleton:
    """Test Database singleton pattern."""

    def test_singleton_same_instance(self):
        """Test that get_instance() returns the same instance."""
        db1 = Database.get_instance()
        db2 = Database.get_instance()
        assert db1 is db2

    def test_singleton_new_method(self):
        """Test that __new__ method returns same instance."""
        db1 = Database()
        db2 = Database()
        assert db1 is db2

    def test_singleton_mixed_access(self):
        """Test that get_instance() and () return same instance."""
        db1 = Database.get_instance()
        db2 = Database()
        assert db1 is db2


class TestDatabaseInitialization:
    """Test Database initialization."""

    def test_is_initialized_before_init(self):
        """Test is_initialized() returns False before init."""
        db = Database.get_instance()
        assert db.is_initialized() is False

    def test_is_initialized_after_init(self, database):
        """Test is_initialized() returns True after init."""
        assert database.is_initialized() is True

    def test_get_engine_returns_engine(self, database):
        """Test get_engine() returns Engine instance."""
        engine = database.get_engine()
        assert isinstance(engine, Engine)

    def test_get_engine_before_init_raises(self):
        """Test get_engine() raises RuntimeError before init."""
        db = Database.get_instance()
        with pytest.raises(RuntimeError, match="Database not initialized"):
            db.get_engine()


class TestDatabaseSession:
    """Test Database session manager."""

    def test_session_yields_session(self, database):
        """Test session() context manager yields Session."""
        with database.session() as session:
            assert session is not None
            assert hasattr(session, "add")
            assert hasattr(session, "commit")
            assert hasattr(session, "rollback")
            assert hasattr(session, "close")

    def test_session_auto_commit(self, database):
        """Test session() automatically commits on success."""
        from sqlalchemy import text

        with database.session() as session:
            session.execute(text("CREATE TABLE test_commit (id INTEGER)"))
            session.execute(text("INSERT INTO test_commit VALUES (1)"))

        with database.session() as session:
            result = session.execute(text("SELECT * FROM test_commit")).fetchall()
            assert len(result) == 1

    def test_session_rollback_on_error(self, database):
        """Test session() rolls back on error."""
        from sqlalchemy import text

        with pytest.raises(Exception):
            with database.session() as session:
                session.execute(text("CREATE TABLE test_rollback (id INTEGER)"))
                session.execute(text("INSERT INTO test_rollback VALUES (1)"))
                raise Exception("Force rollback")

        with database.session() as session:
            result = session.execute(text("SELECT 1")).fetchone()
            assert result[0] == 1


class TestDatabaseTables:
    """Test Database table creation."""

    def test_create_all_tables(self, database):
        """Test create_all_tables() creates tables from Base.metadata."""
        from sqlalchemy import Integer, String
        from sqlalchemy.orm import Mapped, mapped_column
        from typing import Optional
        from madousho.database import Base

        class TestModel(BaseModel):
            __tablename__ = "test_table_create"

            id: Mapped[Optional[int]] = mapped_column(
                Integer, primary_key=True, autoincrement=True, nullable=True
            )
            name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

        database.create_all_tables()
        assert "test_table_create" in Base.metadata.tables

    def test_create_all_tables_before_init_raises(self):
        """Test create_all_tables() raises RuntimeError before init."""
        db = Database.get_instance()
        with pytest.raises(RuntimeError, match="Database not initialized"):
            db.create_all_tables()


class TestDatabaseDispose:
    """Test Database cleanup."""

    def test_dispose_resets_state(self):
        """Test dispose() resets database state."""
        db = Database.get_instance()
        db.init("sqlite:///:memory:")
        assert db.is_initialized() is True

        db.dispose()
        assert db.is_initialized() is False
