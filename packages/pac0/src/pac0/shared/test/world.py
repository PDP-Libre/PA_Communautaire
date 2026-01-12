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
from dataclasses import dataclass
import logging
from typing import Any, Coroutine, Optional, Self, AsyncContextManager

import pytest

from pac0.shared.test.services import NatsService, PaService, PeppolService
from pac0.shared.test.service.dns import DNSServiceContext
from pac0.shared.test.service.pac import PacServiceContext

logger = logging.getLogger(__name__)


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



class WorldContextOld:
    """
    Complete test world with NATS, Peppol, and multiple PA instances.

    The world provides:
    - A shared NATS message broker
    - A PEPPOL lookup service (mock or real)
    - Multiple PA instances (each with API, broker, and services)

    All components implement ServiceProtocol for consistent lifecycle.

    Examples:
        # Simple world with 1 PA
        async with WorldContext(pa_count=1) as world:
            response = await world.pa1.http_client().get("/healthcheck")
            assert response.status_code == 200

        # World with 2 PAs for inter-PA testing
        async with WorldContext(pa_count=2) as world:
            # Both PAs share the same NATS and Peppol services
            assert world.pa1.nats is world.pa2.nats
            assert world.peppol is not None

        # Custom configuration
        async with WorldContext(
            nats_endpoint="nats://external.server:4222",
            peppol_mock=False,
            pa_count=3
        ) as world:
            ...
    """

    def __init__(
        self,
        pa_count: int = 1,
        nats_service: Optional[NatsService] = None,
        nats_endpoint: Optional[str] = None,
        nats_command: Optional[str] = None,
        peppol_service: Optional[PeppolService] = None,
        peppol_mock: bool = True,
        peppol_endpoint: Optional[str] = None,
        ready_timeout: float = 10.0,
    ):
        """
        Initialize the world context.

        Args:
            pa_count: Number of PA instances to create (1-10)
            nats_service: Pre-configured NatsService (takes precedence)
            nats_endpoint: Remote NATS endpoint URL
            nats_command: Command to start local NATS server
            peppol_service: Pre-configured PeppolService (takes precedence)
            peppol_mock: If True, use mock PEPPOL service
            peppol_endpoint: Remote PEPPOL service endpoint
            ready_timeout: Timeout for service readiness
        """
        assert 1 <= pa_count <= 10, "pa_count must be between 1 and 10"

        self._pa_count = pa_count
        self._ready_timeout = ready_timeout

        # Service configuration
        self._nats_service = nats_service
        self._nats_endpoint = nats_endpoint
        self._nats_command = nats_command
        self._owns_nats = nats_service is None

        self._peppol_service = peppol_service
        self._peppol_mock = peppol_mock
        self._peppol_endpoint = peppol_endpoint
        self._owns_peppol = peppol_service is None

        # Services (initialized in __aenter__)
        self.nats: Optional[NatsService] = None
        self.peppol: Optional[PeppolService] = None
        self.pas: list[PaService] = []

        # Named PA references for convenience (pa1, pa2, etc.)
        self.pa1: Optional[PaService] = None
        self.pa2: Optional[PaService] = None
        self.pa3: Optional[PaService] = None
        self.pa4: Optional[PaService] = None
        self.pa5: Optional[PaService] = None
        self.pa6: Optional[PaService] = None
        self.pa7: Optional[PaService] = None
        self.pa8: Optional[PaService] = None
        self.pa9: Optional[PaService] = None
        self.pa10: Optional[PaService] = None

    @property
    def is_running(self) -> bool:
        """Whether all services are running."""
        if not self.nats or not self.nats.is_running:
            return False
        if not self.peppol or not self.peppol.is_running:
            return False
        return all(pa.is_running for pa in self.pas)

    def info(self) -> dict:
        """Return world configuration info."""
        return {
            "nats": {
                "endpoint": self.nats.endpoint if self.nats else None,
                "is_local": self.nats.is_local if self.nats else None,
                "is_running": self.nats.is_running if self.nats else False,
            },
            "peppol": {
                "endpoint": self.peppol.endpoint if self.peppol else None,
                "is_mock": self._peppol_mock,
                "is_running": self.peppol.is_running if self.peppol else False,
            },
            "pas": [
                {
                    "api_base_url": pa.api_base_url,
                    "api_port": pa.api_port,
                    "nats_port": pa.nats_port,
                    "is_running": pa.is_running,
                }
                for pa in self.pas
            ],
        }

    async def __aenter__(self) -> "WorldContextOld":
        """Start all services."""
        # 1. Start NATS service
        if self._nats_service:
            self.nats = self._nats_service
            if not self.nats.is_running:
                await self.nats.__aenter__()
        elif self._nats_endpoint:
            self.nats = NatsService(endpoint=self._nats_endpoint)
            await self.nats.__aenter__()
        elif self._nats_command:
            self.nats = NatsService(command=self._nats_command)
            await self.nats.__aenter__()
        else:
            self.nats = NatsService()  # Embedded
            await self.nats.__aenter__()

        # 2. Start Peppol service
        if self._peppol_service:
            self.peppol = self._peppol_service
            if not self.peppol.is_running:
                await self.peppol.__aenter__()
        elif self._peppol_endpoint:
            self.peppol = PeppolService(
                endpoint=self._peppol_endpoint,
                mock=False,
            )
            await self.peppol.__aenter__()
        else:
            self.peppol = PeppolService(mock=self._peppol_mock)
            await self.peppol.__aenter__()

        # 3. Start PA instances (all share the same NATS)
        for i in range(self._pa_count):
            pa = PaService(
                nats_service=self.nats,
                ready_timeout=self._ready_timeout,
            )
            await pa.__aenter__()
            self.pas.append(pa)

            # Set named reference
            setattr(self, f"pa{i + 1}", pa)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Stop all services in reverse order."""
        # Stop PAs first
        for pa in reversed(self.pas):
            try:
                await pa.__aexit__(exc_type, exc_val, exc_tb)
            except Exception:
                pass
        self.pas.clear()

        # Stop Peppol
        if self._owns_peppol and self.peppol:
            try:
                await self.peppol.__aexit__(exc_type, exc_val, exc_tb)
            except Exception:
                pass
        self.peppol = None

        # Stop NATS last
        if self._owns_nats and self.nats:
            try:
                await self.nats.__aexit__(exc_type, exc_val, exc_tb)
            except Exception:
                pass
        self.nats = None


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture
async def nats_service():
    """Fixture: Isolated NATS service instance."""
    async with NatsService() as svc:
        yield svc


@pytest.fixture
async def peppol_service():
    """Fixture: Mock PEPPOL service instance."""
    async with PeppolService(mock=True) as svc:
        yield svc


@pytest.fixture
async def pa_service():
    """Fixture: Single PA service instance."""
    async with PaService() as svc:
        yield svc


@pytest.fixture
async def world_old():
    """Fixture: World with 1 PA (default)."""
    async with WorldContextOld(pa_count=1) as ctx:
        yield ctx


@pytest.fixture
async def world():
    """Fixture: World"""
    async with WorldContext() as ctx:
        yield ctx
