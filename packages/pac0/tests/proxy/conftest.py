# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Test fixtures for proxy module tests.
"""

import asyncio
import shutil
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Request, Response


# Mock the jose module before importing proxy
@pytest.fixture(autouse=True, scope="session")
def mock_jose():
    """Mock the jose module to allow tests to run without the actual dependency."""
    with patch.dict("sys.modules", {"jose": MagicMock(), "jose.jwt": MagicMock()}):
        yield


@pytest.fixture
def temp_storage_dir():
    """Create a temporary directory for storage backend tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_settings(temp_storage_dir):
    """Create mock settings with proxy enabled."""
    from pac0.service.api_gateway.config import (
        ProxyConfig,
        Settings,
        StoreConfig,
        UpstreamConfig,
    )

    settings = Settings(
        proxy=ProxyConfig(
            enabled=True,
            port=8080,
            upstream=UpstreamConfig(
                endpoint="http://upstream.example.com",
                api_key="test-api-key",
            ),
            store=StoreConfig(
                backend="file",
                path=temp_storage_dir,
            ),
        ),
    )
    return settings


@pytest.fixture
def app(mock_settings):
    """Create a FastAPI app with the proxy router."""
    from pac0.service.api_gateway.lib.proxy import router

    app = FastAPI()
    app.state.conf = mock_settings
    app.include_router(router, prefix="/proxy")
    yield app
    # Cleanup
    import pac0.service.api_gateway.lib.proxy as proxy_module

    proxy_module.config = None


@pytest.fixture
def client(app):
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def create_mock_request():
    """Create a mock HTTP request for testing."""
    mock = MagicMock(spec=Request)
    mock.method = "GET"
    mock.url = MagicMock()
    mock.url.path = "/test/path"
    mock.headers = {"content-type": "application/json", "host": "example.com"}

    async def mock_body():
        return b'{"key": "value"}'

    # Return the async function itself so it can be awaited
    mock.body = mock_body
    return mock


async def get_mock_request():
    """Get a mock HTTP request for testing, returning a resolved body."""
    mock = create_mock_request()

    # Pre-resolve the body so httpx can use it directly
    mock._body = await mock.body()

    # Override the body call to return pre-resolved data
    original_body = mock.body

    async def fixed_body():
        return mock._body

    mock.body = fixed_body
    return mock


@pytest.fixture
async def mock_request():
    """Create a mock HTTP request for testing."""
    return await get_mock_request()


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for testing upstream requests."""
    with patch(
        "pac0.service.api_gateway.lib.proxy.httpx.AsyncClient"
    ) as mock_client_class:
        mock_instance = MagicMock()

        async def mock_request(*args, **kwargs):
            return Response(
                status_code=200,
                content=b'{"success": true}',
                headers={"content-type": "application/json"},
            )

        async def mock_aenter(*args, **kwargs):
            return mock_instance

        async def mock_aexit(*args, **kwargs):
            return None

        mock_instance.request = mock_request
        mock_instance.__aenter__ = mock_aenter
        mock_instance.__aexit__ = mock_aexit

        mock_client_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def settings_with_disabled_proxy(temp_storage_dir):
    """Create settings with proxy disabled."""
    from pac0.service.api_gateway.config import (
        ProxyConfig,
        Settings,
        StoreConfig,
        UpstreamConfig,
    )

    settings = Settings(
        proxy=ProxyConfig(
            enabled=False,
            port=8080,
            upstream=UpstreamConfig(
                endpoint="http://upstream.example.com",
                api_key="test-api-key",
            ),
            store=StoreConfig(
                backend="file",
                path=temp_storage_dir,
            ),
        ),
    )
    return settings
