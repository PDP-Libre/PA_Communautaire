# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tests for WorldContext and service implementations.

Progressive tests from simple service lifecycle to complex multi-PA scenarios:
1. ServiceProtocol compliance
2. Individual service lifecycle (NATS, Peppol, PA)
3. WorldContext basic functionality
4. Multi-PA isolation and communication
5. Service configuration variants (local/remote)

References:
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
- Service Protocol: pac0.shared.test.protocol
"""

import asyncio
import subprocess

import pytest
from faststream.nats import NatsRouter

from pac0.shared.test.protocol import BaseService, ServiceProtocol
from pac0.shared.test.services import (
    NatsService,
    PaService,
    PeppolService,
    ServiceRunner,
)
from pac0.shared.test.world import WorldContext
import logging

# =============================================================================
# Level 5: WorldContext Basic Tests
# =============================================================================

#logging.getLogger().setLevel('DEBUG')

async def test_world_default_0pa():
    """Default WorldContext has no PA."""
    async with WorldContext() as world:
        assert len(world.pas) == 0


async def test_world_with_1pa():
    """WorldContext with 1 PA instance."""
    async with WorldContext() as world:
        await world.pa_new() # default is 1
        assert len(world.pas) == 1

    async with WorldContext() as world:
        await world.pa_new(1)
        assert len(world.pas) == 1


async def test_world_with_4pa():
    """WorldContext with 4 PA instances."""
    async with WorldContext() as world:
        await world.pa_new(4)
        assert len(world.pas) == 4


