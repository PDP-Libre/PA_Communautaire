"""
Pytest configuration for pac0 tests.

Configures pytest-asyncio for proper event loop handling, especially
for BDD tests that need to share async fixtures with sync step functions.

References:
- pytest-asyncio concepts: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
- pytest-asyncio fixtures: https://pytest-asyncio.readthedocs.io/en/latest/how-to-guides/index.html
"""

import asyncio

import pytest


# Re-export fixtures from service_fixture for easy access
from pac0.shared.test.service_fixture import (
    nats_server,
    broker_context,
    pa_service,
    world_service_1pa,
    world_service_2pa,
    world_service_3pa,
    world_service_4pa,
)


@pytest.fixture(scope="session")
def event_loop_policy():
    """
    Use default event loop policy for the session.

    This ensures consistent behavior across different test scenarios.
    """
    return asyncio.DefaultEventLoopPolicy()
