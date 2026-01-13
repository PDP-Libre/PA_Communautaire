# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

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


# Re-export fixtures from the new world module (primary API)
from pac0.shared.test.world import (
    nats_service,
    peppol_service,
    pa_service,
    world,
)

# Re-export fixtures from legacy service_fixture for backward compatibility
from pac0.shared.test.service_fixture import (
    nats_server,
    broker_context,
    pa_service as pa_service_legacy,
)


@pytest.fixture(scope="session")
def event_loop_policy():
    """
    Use default event loop policy for the session.

    This ensures consistent behavior across different test scenarios.
    """
    return asyncio.DefaultEventLoopPolicy()
