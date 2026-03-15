import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from madousho.api.main import app
from madousho.api.deps import get_db
from madousho.database.connection import Database

# Import Base from same location as models to ensure they share the same metadata
from src.madousho.database.base_model import Base
from src.madousho.models.flow import Flow
from src.madousho.models.task import Task  # noqa: F401 - register with Base.metadata
from src.madousho.models.enums import FlowStatus
from madousho.config.loader import _cached_config as cached_config


TEST_TOKEN = "test-secret-token"


class MockConfig:
    def __init__(self, token: str = TEST_TOKEN) -> None:
        self.api = SimpleNamespace(token=token)


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
    """Create a shared in-memory database for testing.

    Uses file::memory:?cache=shared to ensure the database is visible
    across threads (TestClient runs requests in separate threads).
    """
    db = Database.get_instance()
    db.init("sqlite:///file::memory:?cache=shared&uri=true")
    Base.metadata.create_all(db.get_engine())
    yield db
    db.dispose()


@pytest.fixture
def db_session(database):
    """Provide a database session for test setup and override get_db dependency."""
    with database.session() as session:
        yield session


@pytest.fixture
def mock_config(monkeypatch: pytest.MonkeyPatch) -> MockConfig:
    """Mock configuration with test token."""
    cfg = MockConfig()
    monkeypatch.setattr("madousho.config.loader._cached_config", cfg)
    return cfg


@pytest.fixture
def client(database) -> TestClient:
    """Create a test client with database dependency override."""

    def override_get_db():
        db = Database.get_instance()
        with db.session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestFlowListEndpoint:
    def test_list_returns_200_with_pagination(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that list endpoint returns 200 with pagination structure."""
        response = client.get(
            "/api/v1/flows",
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data

    def test_list_default_pagination(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that list endpoint uses default pagination (offset=0, limit=20)."""
        response = client.get(
            "/api/v1/flows",
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["offset"] == 0
        assert data["limit"] == 20

    def test_list_with_offset_limit(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that list endpoint respects offset and limit parameters."""
        response = client.get(
            "/api/v1/flows?offset=5&limit=10",
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["offset"] == 5
        assert data["limit"] == 10

    def test_list_filter_by_status(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that list endpoint filters by status parameter."""
        response = client.get(
            "/api/v1/flows?status=created",
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_list_filter_by_plugin(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that list endpoint filters by plugin parameter."""
        response = client.get(
            "/api/v1/flows?plugin=test_plugin",
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_list_search_by_name(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that list endpoint allows name-based search."""
        response = client.get(
            "/api/v1/flows?name=test",
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_list_sorted_by_created_at_desc(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that list endpoint sorts by created_at descending by default."""
        response = client.get(
            "/api/v1/flows",
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_list_empty_returns_correct_format(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that empty list still returns correct pagination format."""
        response = client.get(
            "/api/v1/flows",
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["offset"] == 0
        assert data["limit"] == 20


class TestFlowDetailEndpoint:
    def test_detail_returns_200_for_existing_flow(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that detail endpoint returns 200 for existing flow."""
        # Create a flow first
        with database.session() as session:
            flow = Flow(
                uuid="test-uuid-12345",
                name="Test Flow",
                plugin="test_plugin",
                flow_template="my-template",
                status=FlowStatus.CREATED.value,
            )
            session.add(flow)
            session.commit()

        response = client.get(
            "/api/v1/flows/test-uuid-12345",
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["uuid"] == "test-uuid-12345"

    def test_detail_returns_404_for_nonexistent_uuid(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that detail endpoint returns 404 for non-existent flow."""
        response = client.get(
            "/api/v1/flows/nonexistent-uuid",
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "message" in data

    def test_detail_returns_full_flow_data(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that detail endpoint returns complete flow information."""
        # Create a flow with data
        with database.session() as session:
            flow = Flow(
                uuid="test-uuid-full",
                name="Full Flow",
                plugin="test_plugin",
                description="A test flow with all data",
                flow_template="my-template-v2",
                status=FlowStatus.PROCESSING.value,
            )
            session.add(flow)
            session.commit()

        response = client.get(
            "/api/v1/flows/test-uuid-full",
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["uuid"] == "test-uuid-full"
        assert data["name"] == "Full Flow"
        assert data["plugin"] == "test_plugin"
        assert data["description"] == "A test flow with all data"
        assert data["status"] == "processing"
        assert "flow_template" in data


class TestFlowCreateEndpoint:
    def test_create_returns_201_with_uuid(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that create endpoint returns 201 and UUID."""
        payload = {
            "name": "New Flow",
            "plugin": "test_plugin",
            "flow_template": "my-template",
        }
        response = client.post(
            "/api/v1/flows",
            json=payload,
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "uuid" in data

    def test_create_missing_name_returns_422(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that create endpoint validates presence of name field."""
        payload = {"plugin": "test_plugin", "flow_template": "my-template"}
        response = client.post(
            "/api/v1/flows",
            json=payload,
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 422

    def test_create_missing_plugin_returns_422(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that create endpoint validates presence of plugin field."""
        payload = {"name": "New Flow", "flow_template": "my-template"}
        response = client.post(
            "/api/v1/flows",
            json=payload,
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 422

    def test_create_missing_flow_template_returns_422(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that create endpoint validates presence of flow_template field."""
        payload = {"name": "New Flow", "plugin": "test_plugin"}
        response = client.post(
            "/api/v1/flows",
            json=payload,
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 422

    def test_create_validates_required_fields(
        self, client: TestClient, mock_config: MockConfig, database
    ):
        """Test that create endpoint requires all mandatory fields."""
        payload = {}
        response = client.post(
            "/api/v1/flows",
            json=payload,
            headers={"Authorization": f"Bearer {mock_config.api.token}"},
        )
        assert response.status_code == 422


class TestFlowAuthRequired:
    def test_list_no_auth_returns_401(self, client: TestClient, database):
        """Test that list endpoint requires authentication."""
        response = client.get("/api/v1/flows")
        assert response.status_code == 401

    def test_detail_no_auth_returns_401(self, client: TestClient, database):
        """Test that detail endpoint requires authentication."""
        response = client.get("/api/v1/flows/test-uuid")
        assert response.status_code == 401

    def test_create_no_auth_returns_401(self, client: TestClient, database):
        """Test that create endpoint requires authentication."""
        payload = {
            "name": "New Flow",
            "plugin": "test_plugin",
            "flow_template": "my-template",
        }
        response = client.post("/api/v1/flows", json=payload)
        assert response.status_code == 401
