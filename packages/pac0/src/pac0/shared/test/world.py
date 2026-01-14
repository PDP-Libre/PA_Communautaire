# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
WorldContext for managing test environments with multiple services.

The world consists of:
- An instance of a NATS service (shared ESB)
- An instance of a Peppol service (for routing)
- Multiple instances of PA services

All services implement the ServiceProtocol for consistent lifecycle management.

References:
- Async Context Managers: https://docs.python.org/3/reference/datamodel.html#async-context-managers
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, AsyncContextManager, Self

import pytest
from pac0.shared.test.service.dns import DNSServiceContext
from pac0.shared.test.service.nats import NatsServiceContext
from pac0.shared.test.service.pac import PacServiceContext

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@dataclass
class WorldContext:
    peppol: DNSServiceContext
    pas: list[PacServiceContext]

    def __init__(
        self,
    ):
        self.peppol = DNSServiceContext()
        self.pas = []
        super().__init__()

    @property
    def pa(self) -> PacServiceContext:
        if len(self.pas) < 1:
            raise IndexError("pa instance not found")
        return self.pas[0]

    @property
    def pa1(self) -> PacServiceContext:
        if len(self.pas) < 1:
            raise IndexError("pa instance not found")
        return self.pas[0]

    @property
    def pa2(self) -> PacServiceContext:
        if len(self.pas) < 2:
            raise IndexError("pa instance not found")
        return self.pas[1]

    async def pa_new(self, count:int = 1) -> PacServiceContext:
        '''
        Add `count` new PA instances to the world context
        Returns the last PA created
        '''
        pas_new = [PacServiceContext() for i in range(count)]
        tasks = [pa.__aenter__() for pa in pas_new]
        await asyncio.gather(*tasks)

        # pa = PacServiceContext()
        # # we enter the new PA context (pa exit is done when on world exit)
        # pa = await pa.__aenter__()

        # self.pas.append(pa)
        self.pas.extend(pas_new)
        return self.pas[-1]

    async def __aenter__(self) -> Self:
        services: list[AsyncContextManager] = [self.peppol, *self.pas]
        await asyncio.gather(*[s.__aenter__() for s in services])
        logger.info("WorldContext: enter context ...")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        services: list[AsyncContextManager] = [self.peppol, *self.pas]
        await asyncio.gather(
            *[s.__aexit__(exc_type, exc_val, exc_tb) for s in services]
        )
        logger.info("WorldContext: exit context ...")


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture
async def nats_service():
    """Fixture: Isolated NATS service instance."""
    async with NatsServiceContext() as svc:
        yield svc


@pytest.fixture
async def world():
    """Fixture: World"""
    async with WorldContext() as ctx:
        yield ctx


@pytest.fixture
async def world1(world):
    """Fixture: World"""
    if len(world.pas) == 0:
        await world.pa_new()
    yield world


# TODO: usefull for async/sync BDD step ??
@pytest.fixture(scope="session")
def event_loop_policy():
    """
    Use default event loop policy for the session.

    This ensures consistent behavior across different test scenarios.
    """
    return asyncio.DefaultEventLoopPolicy()
