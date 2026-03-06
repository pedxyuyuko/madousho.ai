"""Unit tests for FastAPI application creation and configuration."""

import pytest

from madousho.api.app import create_app


class TestAppCreation:
    """Tests for FastAPI application creation."""

    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a FastAPI instance."""
        app = create_app()
        assert app is not None
        assert app.title == "Madousho AI API"

    def test_create_app_has_correct_title(self):
        """Test that the FastAPI app has the correct title."""
        app = create_app()
        assert app.title == "Madousho AI API"

    def test_create_app_has_description(self):
        """Test that the FastAPI app has a description."""
        app = create_app()
        assert app.description is not None
        assert "Systematic AI Agent Framework" in app.description

    def test_create_app_has_version(self):
        """Test that the FastAPI app has a version."""
        app = create_app()
        assert app.version is not None

    def test_create_app_includes_health_router(self):
        """Test that the health check router is included in the app."""
        app = create_app()
        # Check that health route exists
        routes = [route.path for route in app.routes]
        assert "/api/v1/health" in routes

    def test_health_route_is_get_method(self):
        """Test that the health check route accepts GET method."""
        app = create_app()
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/api/v1/health":
                assert 'GET' in route.methods
                break
        else:
            pytest.fail("Health route not found")

    def test_create_app_independent_instances(self):
        """Test that each create_app call returns a new instance."""
        app1 = create_app()
        app2 = create_app()
        assert app1 is not app2


class TestRoutePrefix:
    """Tests for API route prefix configuration."""

    def test_health_route_has_v1_prefix(self):
        """Test that health check route has /api/v1 prefix."""
        app = create_app()
        routes = [route.path for route in app.routes]
        assert "/api/v1/health" in routes

    def test_no_root_health_route(self):
        """Test that there is no health route without version prefix."""
        app = create_app()
        routes = [route.path for route in app.routes]
        assert "/health" not in routes
        assert "api/health" not in routes

    def test_api_v1_prefix_format(self):
        """Test that API routes follow the /api/v1 prefix format."""
        app = create_app()
        for route in app.routes:
            if hasattr(route, 'path') and route.path.startswith('/api'):
                assert route.path.startswith('/api/v1/')

    def test_all_routes_have_api_prefix(self):
        """Test that all functional routes start with /api prefix."""
        app = create_app()
        # Filter out OpenAPI/Swagger routes
        functional_routes = [
            route.path for route in app.routes
            if hasattr(route, 'path') and not route.path.startswith('/openapi')
            and not route.path.startswith('/docs') and not route.path.startswith('/redoc')
        ]
        # All functional routes should start with /api
        for path in functional_routes:
            assert path.startswith('/api')


class TestAppConfiguration:
    """Tests for FastAPI app configuration."""

    def test_app_openapi_url(self):
        """Test that the app has OpenAPI URL configured."""
        app = create_app()
        assert app.openapi_url is not None

    def test_app_docs_urls(self):
        """Test that the app has documentation URLs configured."""
        app = create_app()
        assert app.docs_url is not None
        assert app.redoc_url is not None

    def test_app_routes_count(self):
        """Test that the app has expected number of routes."""
        app = create_app()
        # Should have at least: health, openapi.json, docs, redoc
        assert len(app.routes) >= 4

    def test_app_lifespan_context(self):
        """Test that the app supports lifespan context."""
        app = create_app()
        # FastAPI apps should support lifespan context manager
        assert hasattr(app, 'router') and hasattr(app.router, 'lifespan_context')

    def test_app_exception_handlers(self):
        """Test that the app has exception handlers configured."""
        app = create_app()
        # FastAPI apps should have exception handlers
        assert hasattr(app, 'exception_handlers')

    def test_app_middleware_stack(self):
        """Test that the app has middleware stack."""
        app = create_app()
        # FastAPI apps should have middleware stack
        assert hasattr(app, 'middleware_stack')

    def test_app_debug_setting(self):
        """Test that the app debug setting is accessible."""
        app = create_app()
        # Debug should be accessible
        assert hasattr(app, 'debug')

    def test_app_state_attribute(self):
        """Test that the app has state attribute for storing app-level state."""
        app = create_app()
        # FastAPI apps should have state attribute
        assert hasattr(app, 'state')

    def test_app_state_isolation(self):
        """Test that app state is isolated between instances."""
        app1 = create_app()
        app2 = create_app()
        # Each app should have its own state
        assert app1.state is not app2.state

    def test_app_metadata(self):
        """Test that the app has metadata dictionary."""
        app = create_app()
        # FastAPI apps have title, version, etc. as metadata
        assert hasattr(app, 'title')
        assert hasattr(app, 'version')

    def test_app_can_add_custom_routes(self):
        """Test that custom routes can be added to the app."""
        app = create_app()
        from fastapi import APIRouter
        
        custom_router = APIRouter(prefix="/custom")
        
        @custom_router.get("/test")
        async def test_endpoint():
            return {"test": "ok"}
        
        app.include_router(custom_router)
        routes = [route.path for route in app.routes]
        assert "/custom/test" in routes

    def test_app_cors_middleware_can_be_added(self):
        """Test that CORS middleware can be added to the app."""
        app = create_app()
        from fastapi.middleware.cors import CORSMiddleware
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        # If we get here without error, CORS was added successfully
        assert True


class TestHealthEndpoint:
    """Tests for health check endpoint behavior."""

    def test_health_endpoint_exists(self):
        """Test that health endpoint route exists."""
        app = create_app()
        routes = [route.path for route in app.routes]
        assert "/api/v1/health" in routes

    def test_health_endpoint_methods(self):
        """Test that health endpoint only accepts GET method."""
        app = create_app()
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/api/v1/health":
                assert route.methods == {'GET'}
                break
        else:
            pytest.fail("Health route not found")

    def test_health_endpoint_tags(self):
        """Test that health endpoint may have tags configured."""
        app = create_app()
        # Tags are optional, but route should exist
        for route in app.routes:
            if hasattr(route, 'path') and route.path == "/api/v1/health":
                # Route exists, tags are optional
                assert True
                break
        else:
            pytest.fail("Health route not found")


class TestAppVersion:
    """Tests for application version handling."""

    def test_version_is_not_none(self):
        """Test that app version is not None."""
        app = create_app()
        assert app.version is not None

    def test_version_is_string(self):
        """Test that app version is a string."""
        app = create_app()
        assert isinstance(app.version, str)

    def test_version_format(self):
        """Test that app version follows semantic versioning format."""
        app = create_app()
        import re
        # Semantic versioning pattern (major.minor.patch with optional suffix)
        pattern = r'^\d+\.\d+\.\d+.*'
        assert re.match(pattern, app.version) is not None



class TestVersionImport:
    """Tests for version import fallback logic."""

    def test_version_import_from_version_module(self):
        """Test that version is imported from _version module normally."""
        app = create_app()
        # Version should be imported successfully from _version
        assert app.version is not None
        assert isinstance(app.version, str)

    def test_version_fallback_logic_exists(self):
        """Test that the fallback version logic exists in app.py."""
        # Verify the fallback code exists by checking the source
        import inspect
        from madousho.api import app as app_module
        source = inspect.getsource(app_module)
        # Fallback version should be in source
        assert '__version__ = "0.1.0"' in source
        assert 'except ImportError:' in source



class TestHealthRoute:
    """Tests for health route functionality."""

    @pytest.mark.asyncio
    async def test_health_check_endpoint_returns_status(self):
        """Test that health check endpoint returns status and version."""
        from madousho.api.routes.health import health_check
        result = await health_check()
        assert result["status"] == "ok"
        assert "version" in result

    def test_health_router_has_correct_prefix(self):
        """Test that health router has the correct path."""
        from madousho.api.routes.health import router
        for route in router.routes:
            if hasattr(route, 'path'):
                assert route.path == "/api/v1/health"
