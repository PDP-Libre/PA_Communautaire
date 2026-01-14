# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Service lifecycle fixtures with proper readiness detection.

This module provides improved test fixtures that use FastStream's @app.after_startup
hook to detect service readiness instead of arbitrary sleep delays.

References:
- FastStream Lifespan Hooks: https://faststream.ag2.ai/latest/getting-started/lifespan/hooks/
- FastStream Testing: https://faststream.ag2.ai/latest/getting-started/lifespan/test/
- FastStream Health Checks: https://faststream.ag2.ai/latest/getting-started/observability/healthcheks/
- Async Context Managers: https://medium.com/@hitorunajp/asynchronous-context-managers-f1c33d38c9e3
- NATS Python Server: https://github.com/nats-io/nats.py/tree/main/nats-server
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
"""

import asyncio
from typing import Optional

import httpx
import pytest
from fastapi import FastAPI
from faststream import FastStream
from faststream.nats import NatsBroker, NatsRouter
from nats.server import run as nats_run

# from pac0.service.api_gateway.lib import router as router_api_gateway
# from pac0.service.gestion_cycle_vie.lib import router as router_gestion_cycle_vie
# from pac0.service.validation_metier.lib import router as router_validation_metier
from pac0.shared.tools.api import uvicorn_context


# Default timeout for service readiness (seconds)
DEFAULT_READY_TIMEOUT = 10.0


class ServiceRunner:
    """
    Wrapper for a FastStream service with readiness detection.

    Uses @app.after_startup hook to signal when the service is ready,
    eliminating the need for arbitrary sleep delays.

    Hook execution order (from FastStream docs):
    1. on_startup    - before broker connected
    2. after_startup - after broker connected (service is READY here)
    3. on_shutdown   - before broker disconnected
    4. after_shutdown - after broker disconnected

    Example:
        runner = ServiceRunner(broker, router, name="validation-metier")
        task = await runner.start()
        await runner.wait_ready(timeout=5.0)
        # Service is now ready to process messages

    See: https://faststream.ag2.ai/latest/getting-started/lifespan/hooks/
    """

    def __init__(
        self,
        broker: NatsBroker,
        router: NatsRouter,
        name: str = "service",
    ):
        self.name = name
        self.broker = broker
        self.router = router
        self.ready = asyncio.Event()
        self.task: Optional[asyncio.Task] = None

        # Create FastStream app and register router
        self.app = FastStream(broker)
        broker.include_router(router)

        # Register after_startup hook to signal readiness
        # This is called AFTER the broker is connected and ready
        @self.app.after_startup
        async def _signal_ready():
            self.ready.set()

    async def start(self) -> asyncio.Task:
        """
        Start the service as a background task.

        Returns:
            asyncio.Task: The running service task
        """
        self.task = asyncio.create_task(self.app.run(), name=f"service-{self.name}")
        return self.task

    async def wait_ready(self, timeout: float = DEFAULT_READY_TIMEOUT) -> None:
        """
        Wait for the service to be ready.

        Args:
            timeout: Maximum time to wait in seconds

        Raises:
            asyncio.TimeoutError: If service doesn't become ready within timeout
        """
        await asyncio.wait_for(self.ready.wait(), timeout=timeout)

    async def stop(self) -> None:
        """Stop the service gracefully."""
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None


class NatsServerContext:
    """
    Async context manager for NATS server lifecycle.

    Uses dynamic port allocation (port=0) for test isolation.

    Example:
        async with NatsServerContext() as ctx:
            print(f"NATS running on port {ctx.port}")

    See: https://github.com/nats-io/nats.py/tree/main/nats-server
    """

    def __init__(self):
        self._server = None
        self.host: str = ""
        self.port: int = 0
        self.url: str = ""

    @property
    def is_running(self) -> bool:
        return self._server is not None and self._server.is_running

    async def __aenter__(self):
        # Start NATS with dynamic port allocation
        self._server = await nats_run(port=0)
        await self._server.__aenter__()

        self.host = self._server.host
        self.port = self._server.port
        self.url = f"nats://{self.host}:{self.port}"

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._server:
            try:
                await self._server.__aexit__(exc_type, exc_val, exc_tb)
            except Exception:
                pass


class BrokerContext:
    """
    Async context manager for NatsBroker lifecycle.

    Wraps NatsBroker with proper connection management.

    Example:
        async with NatsServerContext() as nats:
            async with BrokerContext(nats.url) as ctx:
                await ctx.broker.publish("hello", "test-subject")
    """

    def __init__(self, nats_url: str):
        self.nats_url = nats_url
        self._broker: Optional[NatsBroker] = None
        self.broker: Optional[NatsBroker] = None
        self.wildcard_subscriber = None

    async def __aenter__(self):
        self._broker = NatsBroker(self.nats_url, apply_types=True)
        self.broker = await self._broker.__aenter__()

        # Create wildcard subscriber for message inspection
        self.wildcard_subscriber = self.broker.subscriber(">")

        await self.broker.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.broker:
            try:
                await self.broker.__aexit__(exc_type, exc_val, exc_tb)
            except Exception:
                pass


class ServicePoolContext:
    """
    Async context manager for multiple FastStream services.

    Starts all services and waits for them to be ready before yielding.

    Example:
        routers = [router_validation, router_gestion]
        async with ServicePoolContext(broker, routers) as pool:
            # All services are ready
            await broker.publish(msg, "validation-metier-IN")
    """

    def __init__(
        self,
        broker: NatsBroker,
        routers: list[tuple[NatsRouter, str]],
        ready_timeout: float = DEFAULT_READY_TIMEOUT,
    ):
        """
        Args:
            broker: The NatsBroker instance to use
            routers: List of (router, name) tuples
            ready_timeout: Timeout for each service to become ready
        """
        self.broker = broker
        self.ready_timeout = ready_timeout
        self.runners: list[ServiceRunner] = []

        for router, name in routers:
            self.runners.append(ServiceRunner(broker, router, name))

    async def __aenter__(self):
        # Start all services
        for runner in self.runners:
            await runner.start()

        # Wait for all services to be ready (with timeout)
        await asyncio.gather(
            *[runner.wait_ready(timeout=self.ready_timeout) for runner in self.runners]
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Stop all services
        for runner in self.runners:
            await runner.stop()


# TODO: obsolete
class PaServiceContext:
    """
    Complete PA (Plateforme Agreee) context with all components.

    Includes:
    - NATS server (dynamic port)
    - NatsBroker client
    - FastAPI gateway (dynamic port)
    - FastStream services (validation, gestion cycle vie)

    Uses @app.after_startup hooks for proper readiness detection.

    Example:
        async with PaServiceContext() as pa:
            async with pa.http_client() as client:
                response = await client.get("/healthcheck")
                assert response.status_code == 200

    See: https://medium.com/@hitorunajp/asynchronous-context-managers-f1c33d38c9e3
    """

    # Default routers to load
    DEFAULT_ROUTERS = [
        # (router_validation_metier, "validation-metier"),
        # (router_gestion_cycle_vie, "gestion-cycle-vie"),
    ]

    def __init__(
        self,
        routers: Optional[list[tuple[NatsRouter, str]]] = None,
        ready_timeout: float = DEFAULT_READY_TIMEOUT,
    ):
        self.routers = routers or self.DEFAULT_ROUTERS
        self.ready_timeout = ready_timeout

        # Components (initialized in __aenter__)
        self._nats_ctx: Optional[NatsServerContext] = None
        self._broker_ctx: Optional[BrokerContext] = None
        self._service_pool: Optional[ServicePoolContext] = None
        self._uvicorn_ctx = None

        # Public attributes
        self.nats: Optional[NatsServerContext] = None
        self.broker: Optional[NatsBroker] = None
        self.api_base_url: str = ""
        self.uvicorn_server = None

    async def __aenter__(self):
        # 1. Start NATS server
        self._nats_ctx = NatsServerContext()
        self.nats = await self._nats_ctx.__aenter__()

        # 2. Connect broker
        self._broker_ctx = BrokerContext(self.nats.url)
        broker_ctx = await self._broker_ctx.__aenter__()
        self.broker = broker_ctx.broker

        # 3. Start FastAPI gateway
        app = FastAPI()
        app.state.rank = "test"
        app.state.broker = self._broker_ctx._broker
        app.include_router(router_api_gateway)

        self._uvicorn_ctx = uvicorn_context(app, port=0)
        self.uvicorn_server = await self._uvicorn_ctx.__aenter__()
        self.api_base_url = f"http://{self.uvicorn_server.config.host}:{self.uvicorn_server.config.port}"

        # 4. Start FastStream services with readiness detection
        self._service_pool = ServicePoolContext(
            self.broker,
            self.routers,
            ready_timeout=self.ready_timeout,
        )
        await self._service_pool.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Stop in reverse order
        if self._service_pool:
            await self._service_pool.__aexit__(exc_type, exc_val, exc_tb)

        if self._uvicorn_ctx:
            await self._uvicorn_ctx.__aexit__(exc_type, exc_val, exc_tb)

        if self._broker_ctx:
            await self._broker_ctx.__aexit__(exc_type, exc_val, exc_tb)

        if self._nats_ctx:
            await self._nats_ctx.__aexit__(exc_type, exc_val, exc_tb)

    def http_client(self) -> httpx.AsyncClient:
        """Get an async HTTP client configured for this PA's API."""
        return httpx.AsyncClient(base_url=self.api_base_url)

    def info(self) -> dict:
        """Return connection info for debugging."""
        return {
            "nats_url": self.nats.url if self.nats else None,
            "nats_port": self.nats.port if self.nats else None,
            "api_base_url": self.api_base_url,
            "api_port": self.uvicorn_server.config.port
            if self.uvicorn_server
            else None,
        }


class WorldServiceContext:
    """
    Multiple PA instances for testing multi-platform scenarios.

    Each PA has its own isolated:
    - NATS server
    - Broker connection
    - FastAPI gateway
    - FastStream services

    Example:
        async with WorldServiceContext(pac_count=2) as world:
            # Test cross-PA communication
            pa1_url = world.pac1.api_base_url
            pa2_url = world.pac2.api_base_url
    """

    def __init__(
        self,
        pac_count: int = 1,
        ready_timeout: float = DEFAULT_READY_TIMEOUT,
    ):
        assert 1 <= pac_count <= 4, "pac_count must be between 1 and 4"

        self.pac_count = pac_count
        self.ready_timeout = ready_timeout
        self.pacs: list[PaServiceContext] = []

        # Named references for convenience
        self.pac1: Optional[PaServiceContext] = None
        self.pac2: Optional[PaServiceContext] = None
        self.pac3: Optional[PaServiceContext] = None
        self.pac4: Optional[PaServiceContext] = None

    async def __aenter__(self):
        # Create PA instances
        for i in range(self.pac_count):
            pac = PaServiceContext(ready_timeout=self.ready_timeout)
            self.pacs.append(pac)
            setattr(self, f"pac{i + 1}", pac)

        # Start all PAs concurrently for faster startup
        await asyncio.gather(*[pac.__aenter__() for pac in self.pacs])

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Stop all PAs concurrently
        await asyncio.gather(
            *[pac.__aexit__(exc_type, exc_val, exc_tb) for pac in self.pacs],
            return_exceptions=True,
        )


# ============================================================================
# Pytest fixtures
# ============================================================================


@pytest.fixture
async def nats_server():
    """Fixture: Isolated NATS server instance."""
    async with NatsServerContext() as ctx:
        yield ctx


@pytest.fixture
async def broker_context(nats_server):
    """Fixture: NatsBroker connected to test NATS server."""
    async with BrokerContext(nats_server.url) as ctx:
        yield ctx


@pytest.fixture
async def pa_service():
    """Fixture: Complete PA with all services ready."""
    async with PaServiceContext() as pa:
        yield pa


@pytest.fixture
async def world_service_1pa():
    """Fixture: World with 1 PA instance."""
    async with WorldServiceContext(pac_count=1) as world:
        yield world


@pytest.fixture
async def world_service_2pa():
    """Fixture: World with 2 PA instances."""
    async with WorldServiceContext(pac_count=2) as world:
        yield world


@pytest.fixture
async def world_service_3pa():
    """Fixture: World with 3 PA instances."""
    async with WorldServiceContext(pac_count=3) as world:
        yield world


@pytest.fixture
async def world_service_4pa():
    """Fixture: World with 4 PA instances."""
    async with WorldServiceContext(pac_count=4) as world:
        yield world
