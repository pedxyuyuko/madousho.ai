"""Unit tests for Flow model's status and flow_template fields."""

import pytest
from sqlalchemy import String

from madousho.database import Database

# Import Base from same location as models to ensure they share the same metadata
from src.madousho.database.base_model import Base
from src.madousho.models.flow import Flow
from src.madousho.models.task import Task  # noqa: F401 - register with Base.metadata


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset Database singleton before and after each test."""
    Database._instance = None
    Database._engine = None
    Database._session_factory = None
    yield
    Database._instance = None
    Database._engine = None
    Database._session_factory = None


@pytest.fixture
def database():
    """Create and setup in-memory SQLite database for testing."""
    db = Database.get_instance()
    db.init("sqlite:///:memory:")
    # Use Base.metadata directly to create tables (same Base as models)
    Base.metadata.create_all(db.get_engine())
    yield db
    db.dispose()


class TestFlowModel:
    """Unit tests for Flow model's new status and flow_template fields."""

    def test_flow_has_status_field(self):
        """Test that Flow model has status column."""
        assert hasattr(Flow, "status")
        column_type = Flow.__table__.columns["status"].type
        assert isinstance(column_type, String)
        assert column_type.length == 20
        assert not Flow.__table__.columns["status"].nullable

    def test_flow_has_flow_template_field(self):
        """Test that Flow model has flow_template column."""
        assert hasattr(Flow, "flow_template")
        column_type = Flow.__table__.columns["flow_template"].type
        assert isinstance(column_type, String)
        assert column_type.length == 255
        assert Flow.__table__.columns["flow_template"].nullable

    def test_status_default_value(self, database):
        """Test that status field defaults to 'created' when saved to database."""
        flow = Flow(name="Test Flow", description="A test flow", plugin="test_plugin")
        with database.session() as session:
            session.add(flow)
            session.commit()

            retrieved_flow = session.query(Flow).filter_by(uuid=flow.uuid).first()
            assert retrieved_flow.status == "created"

    def test_status_values(self, database):
        """Test that flow can be created with different status values."""
        status_values = ["created", "processing", "finished"]

        for i, status_val in enumerate(status_values):
            flow = Flow(
                name=f"Test Flow {i}",
                description="A test flow",
                plugin="test_plugin",
                status=status_val,
            )

            with database.session() as session:
                session.add(flow)
                session.commit()

                retrieved_flow = session.query(Flow).filter_by(uuid=flow.uuid).first()
                assert retrieved_flow.status == status_val

    def test_flow_template_nullable(self, database):
        """Test that flow_template field can be None."""
        flow = Flow(
            name="Test Flow",
            description="A test flow with null template",
            plugin="test_plugin",
            flow_template=None,
        )

        with database.session() as session:
            session.add(flow)
            session.commit()

            retrieved_flow = session.query(Flow).filter_by(uuid=flow.uuid).first()
            assert retrieved_flow.flow_template is None

    def test_flow_template_value(self, database):
        """Test that flow_template field can store values."""
        template_name = "my-template-v1"
        flow = Flow(
            name="Test Flow",
            description="A test flow with template",
            plugin="test_plugin",
            flow_template=template_name,
        )

        with database.session() as session:
            session.add(flow)
            session.commit()

            retrieved_flow = session.query(Flow).filter_by(uuid=flow.uuid).first()
            assert retrieved_flow.flow_template == template_name

    def test_create_flow_with_status(self, database):
        """Test creating and retrieving a flow with specific status."""
        flow = Flow(
            name="Test Flow",
            description="Test flow with processing status",
            plugin="test_plugin",
            status="processing",
        )

        with database.session() as session:
            session.add(flow)
            session.commit()

            retrieved_flow = session.query(Flow).filter_by(uuid=flow.uuid).first()
            assert retrieved_flow.uuid == flow.uuid
            assert retrieved_flow.name == "Test Flow"
            assert retrieved_flow.status == "processing"
            assert retrieved_flow.flow_template is None
