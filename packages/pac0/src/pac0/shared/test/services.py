"""
Service implementations for NATS, Peppol, and PA.

This module provides concrete implementations of the ServiceProtocol
for the three types of services used in the PA ecosystem:

- NatsService: NATS message broker (local subprocess or remote)
- PeppolService: PEPPOL lookup service (mock or real)
- PaService: Complete PA instance (API + services + broker)

References:
- NATS Server: https://nats.io/
- FastStream: https://faststream.ag2.ai/
- FastAPI: https://fastapi.tiangolo.com/
"""

import asyncio
import shlex
import subprocess
from typing import Optional

import httpx
from fastapi import FastAPI
from faststream import FastStream
from faststream.nats import NatsBroker, NatsRouter
from nats.server import run as nats_run

from pac0.service.api_gateway.lib import router as router_api_gateway
from pac0.service.gestion_cycle_vie.lib import router as router_gestion_cycle_vie
from pac0.service.routage.lib import router as router_routage
from pac0.service.routage.peppol import (
    PeppolEndpoint,
    PeppolEnvironment,
    PeppolLookupResult,
    PeppolLookupService,
)
from pac0.service.validation_metier.lib import router as router_validation_metier
from pac0.shared.test.protocol import BaseService
from pac0.shared.tools.api import uvicorn_context


# Default timeout for service readiness (seconds)
DEFAULT_READY_TIMEOUT = 10.0


class NatsService(BaseService):
    """
    NATS message broker service.

    Can be started either:
    - Locally via embedded Python NATS server (port=0 for dynamic port)
    - Locally via command string (e.g., "nats-server -p 4222")
    - Remotely by connecting to existing endpoint

    Examples:
        # Embedded local server (recommended for tests)
        async with NatsService() as nats:
            print(nats.endpoint)  # nats://localhost:12345

        # Local server via command
        async with NatsService(command="nats-server -p 0 -js") as nats:
            print(nats.endpoint)

        # Remote server
        async with NatsService(endpoint="nats://ebs.dev.paxpar.tech") as nats:
            print(nats.endpoint)
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        command: Optional[str] = None,
        use_embedded: bool = True,
    ):
        """
        Initialize NATS service.

        Args:
            endpoint: Remote NATS endpoint URL
            command: Command to start local NATS server
            use_embedded: If True and no endpoint/command, use embedded Python NATS server

        If neither endpoint nor command is provided and use_embedded is True,
        an embedded NATS server is started with a dynamic port.
        """
        # If no explicit config, use embedded server
        if not endpoint and not command and use_embedded:
            self._use_embedded = True
            super().__init__(command="__embedded__")
        else:
            self._use_embedded = False
            super().__init__(endpoint=endpoint, command=command)

        self._nats_server = None
        self._host = "localhost"
        self._port = 0

    @property
    def host(self) -> str:
        """NATS server host."""
        return self._host

    @property
    def port(self) -> int:
        """NATS server port."""
        return self._port

    async def _start_local(self) -> None:
        """Start local NATS server."""
        if self._use_embedded:
            # Use embedded Python NATS server
            self._nats_server = await nats_run(port=0)
            await self._nats_server.__aenter__()
            self._host = self._nats_server.host
            self._port = self._nats_server.port
            self._endpoint = f"nats://{self._host}:{self._port}"
        else:
            # Start via command string
            args = shlex.split(self._command)
            self._process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # Parse port from command or wait for startup message
            # For simplicity, assume port 4222 if not specified
            self._port = 4222
            for arg in args:
                if arg.startswith("-p"):
                    try:
                        self._port = int(arg[2:])
                    except ValueError:
                        pass
                elif arg.isdigit() and args[args.index(arg) - 1] == "-p":
                    self._port = int(arg)
            self._endpoint = f"nats://{self._host}:{self._port}"

    async def _stop_local(self) -> None:
        """Stop local NATS server."""
        if self._use_embedded and self._nats_server:
            try:
                await self._nats_server.__aexit__(None, None, None)
            except Exception:
                pass
            self._nats_server = None
        elif self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    async def _connect_remote(self) -> None:
        """Connect to remote NATS server."""
        # Parse host/port from endpoint
        # Format: nats://host:port
        url = self._endpoint
        if url.startswith("nats://"):
            url = url[7:]
        if ":" in url:
            self._host, port_str = url.split(":")
            self._port = int(port_str)
        else:
            self._host = url
            self._port = 4222

    async def _wait_for_ready(self, timeout: float = 5.0) -> None:
        """Wait for NATS server to be ready."""
        if self._use_embedded:
            # Embedded server is ready immediately after start
            return

        # For subprocess or remote, try to connect
        from nats.aio.client import Client

        nc = Client()
        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            try:
                await asyncio.wait_for(
                    nc.connect(self._endpoint, connect_timeout=0.5),
                    timeout=1.0,
                )
                await nc.close()
                return
            except Exception:
                await asyncio.sleep(0.1)
        raise asyncio.TimeoutError(f"NATS server not ready at {self._endpoint}")


class PeppolService(BaseService):
    """
    PEPPOL lookup service.

    Can operate in two modes:
    - Mock mode: Uses in-memory mock responses (for testing)
    - Real mode: Connects to actual PEPPOL SML/SMP infrastructure

    Examples:
        # Mock service (for tests)
        async with PeppolService(mock=True) as peppol:
            peppol.set_mock_response("0009", "123456789", endpoint)

        # Real service (test environment)
        async with PeppolService(environment=PeppolEnvironment.TEST) as peppol:
            result = await peppol.lookup_by_siren("123456789")

        # Remote service endpoint
        async with PeppolService(endpoint="https://peppol.example.com") as peppol:
            ...
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        command: Optional[str] = None,
        mock: bool = True,
        environment: PeppolEnvironment = PeppolEnvironment.TEST,
    ):
        """
        Initialize PEPPOL service.

        Args:
            endpoint: Remote PEPPOL service endpoint (if using external service)
            command: Command to start local PEPPOL server (if using subprocess)
            mock: If True, use mock mode (in-memory responses)
            environment: PEPPOL environment (TEST or PRODUCTION)
        """
        # Mock mode doesn't need endpoint or command
        if mock and not endpoint and not command:
            super().__init__(endpoint="mock://peppol")
            self._mock = True
        else:
            super().__init__(endpoint=endpoint, command=command)
            self._mock = mock

        self._environment = environment
        self._lookup_service: Optional[PeppolLookupService] = None

    @property
    def lookup_service(self) -> PeppolLookupService:
        """Get the underlying PEPPOL lookup service."""
        if not self._lookup_service:
            raise RuntimeError("PEPPOL service not started")
        return self._lookup_service

    def set_mock_response(
        self,
        scheme_id: str,
        participant_id: str,
        smp_url: Optional[str] = "https://smp.mock.peppol",
        endpoint: Optional[PeppolEndpoint] = None,
        error_code: Optional[str] = None,
    ) -> None:
        """
        Set a mock response for a participant.

        Args:
            scheme_id: PEPPOL scheme ID (e.g., "0009" for SIREN)
            participant_id: Participant identifier
            smp_url: Mock SMP URL
            endpoint: Mock endpoint to return
            error_code: Error code to simulate (e.g., "PARTICIPANT_NOT_FOUND")
        """
        if not self._lookup_service:
            raise RuntimeError("PEPPOL service not started")
        self._lookup_service.set_mock_smp_response(
            scheme_id, participant_id, smp_url, endpoint, error_code
        )

    def clear_mock_responses(self) -> None:
        """Clear all mock responses."""
        if self._lookup_service:
            self._lookup_service.clear_mock_responses()

    async def lookup_by_siren(
        self, siren: str, document_type: str = "invoice_ubl"
    ) -> PeppolLookupResult:
        """Lookup by SIREN."""
        return await self._lookup_service.lookup_by_siren(siren, document_type)

    async def lookup_by_siret(
        self, siret: str, document_type: str = "invoice_ubl"
    ) -> PeppolLookupResult:
        """Lookup by SIRET."""
        return await self._lookup_service.lookup_by_siret(siret, document_type)

    async def _start_local(self) -> None:
        """Start local PEPPOL service (subprocess mode)."""
        if self._command and self._command != "__mock__":
            args = shlex.split(self._command)
            self._process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        # Initialize lookup service
        self._lookup_service = PeppolLookupService(
            environment=self._environment,
        )

    async def _stop_local(self) -> None:
        """Stop local PEPPOL service."""
        if self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    async def _connect_remote(self) -> None:
        """Connect to remote PEPPOL service."""
        # For mock mode, just create the lookup service
        if self._mock:
            self._lookup_service = PeppolLookupService(
                environment=self._environment,
            )
        else:
            # Real mode with remote endpoint would use HTTP client
            self._lookup_service = PeppolLookupService(
                environment=self._environment,
            )

    async def _wait_for_ready(self) -> None:
        """Wait for PEPPOL service to be ready."""
        # Mock service is always ready
        if self._mock:
            return
        # For subprocess, wait for process
        if self._process:
            await asyncio.sleep(0.5)
        # For remote, try a test request
        if not self._mock and self._endpoint and self._endpoint != "mock://peppol":
            async with httpx.AsyncClient() as client:
                max_retries = 30
                for _ in range(max_retries):
                    try:
                        response = await client.get(
                            f"{self._endpoint}/health", timeout=1
                        )
                        if response.status_code == 200:
                            return
                    except Exception:
                        await asyncio.sleep(0.1)
                raise asyncio.TimeoutError(
                    f"PEPPOL service not ready at {self._endpoint}"
                )


class ServiceRunner:
    """
    Wrapper for a FastStream service with readiness detection.

    Uses @app.after_startup hook to signal when the service is ready.
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
        @self.app.after_startup
        async def _signal_ready():
            self.ready.set()

    async def start(self) -> asyncio.Task:
        """Start the service as a background task."""
        self.task = asyncio.create_task(self.app.run(), name=f"service-{self.name}")
        return self.task

    async def wait_ready(self, timeout: float = DEFAULT_READY_TIMEOUT) -> None:
        """Wait for the service to be ready."""
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


class PaService(BaseService):
    """
    Complete PA (Plateforme Agreee) service.

    Includes:
    - NATS broker connection
    - FastAPI gateway
    - FastStream services (validation, gestion cycle vie, routage)

    Examples:
        # Local PA with embedded NATS
        async with PaService(nats_service=NatsService()) as pa:
            async with pa.http_client() as client:
                response = await client.get("/healthcheck")

        # PA connecting to external NATS
        async with PaService(nats_endpoint="nats://ebs.dev.paxpar.tech") as pa:
            ...
    """

    # Default routers to load
    DEFAULT_ROUTERS = [
        (router_validation_metier, "validation-metier"),
        (router_gestion_cycle_vie, "gestion-cycle-vie"),
        (router_routage, "routage"),
    ]

    def __init__(
        self,
        endpoint: Optional[str] = None,
        command: Optional[str] = None,
        nats_service: Optional[NatsService] = None,
        nats_endpoint: Optional[str] = None,
        routers: Optional[list[tuple[NatsRouter, str]]] = None,
        ready_timeout: float = DEFAULT_READY_TIMEOUT,
    ):
        """
        Initialize PA service.

        Args:
            endpoint: Remote PA API endpoint (if connecting to existing PA)
            command: Command to start PA (if using subprocess)
            nats_service: NatsService instance to use (takes precedence)
            nats_endpoint: NATS endpoint URL (creates new NatsService)
            routers: List of (router, name) tuples for FastStream services
            ready_timeout: Timeout for service readiness
        """
        # PA is "local" when we don't have an endpoint to connect to
        # Use a marker command to indicate local mode
        if not endpoint:
            command = command or "__local_pa__"
        super().__init__(endpoint=endpoint, command=command)

        self._nats_service = nats_service
        self._nats_endpoint = nats_endpoint
        self._owns_nats = nats_service is None and nats_endpoint is None
        self._routers = routers or self.DEFAULT_ROUTERS
        self._ready_timeout = ready_timeout

        # Components (initialized in __aenter__)
        self._broker: Optional[NatsBroker] = None
        self._uvicorn_ctx = None
        self._service_runners: list[ServiceRunner] = []

        # Public attributes
        self.broker: Optional[NatsBroker] = None
        self.api_base_url: str = ""
        self.uvicorn_server = None
        self.nats: Optional[NatsService] = None

    @property
    def api_port(self) -> int:
        """API server port."""
        return self.uvicorn_server.config.port if self.uvicorn_server else 0

    @property
    def nats_port(self) -> int:
        """NATS server port."""
        return self.nats.port if self.nats else 0

    def http_client(self) -> httpx.AsyncClient:
        """Get an async HTTP client configured for this PA's API."""
        return httpx.AsyncClient(base_url=self.api_base_url)

    def info(self) -> dict:
        """Return connection info for debugging."""
        return {
            "nats_url": self.nats.endpoint if self.nats else None,
            "nats_port": self.nats.port if self.nats else None,
            "api_base_url": self.api_base_url,
            "api_port": self.api_port,
        }

    async def _start_local(self) -> None:
        """Start local PA components."""
        # 1. Setup NATS
        if self._nats_service:
            self.nats = self._nats_service
        elif self._nats_endpoint:
            self.nats = NatsService(endpoint=self._nats_endpoint)
        else:
            self.nats = NatsService()  # Embedded

        # Start NATS if we own it
        if self._owns_nats or self._nats_endpoint:
            await self.nats.__aenter__()

        # 2. Connect broker
        self._broker = NatsBroker(self.nats.endpoint, apply_types=True)
        self.broker = await self._broker.__aenter__()
        await self.broker.start()

        # 3. Start FastAPI gateway
        app = FastAPI()
        app.state.rank = "test"
        app.state.broker = self._broker
        app.include_router(router_api_gateway)

        self._uvicorn_ctx = uvicorn_context(app, port=0)
        self.uvicorn_server = await self._uvicorn_ctx.__aenter__()
        self.api_base_url = f"http://{self.uvicorn_server.config.host}:{self.uvicorn_server.config.port}"
        self._endpoint = self.api_base_url

        # 4. Start FastStream services
        for router, name in self._routers:
            runner = ServiceRunner(self.broker, router, name)
            await runner.start()
            self._service_runners.append(runner)

    async def _stop_local(self) -> None:
        """Stop local PA components."""
        # Stop services
        for runner in self._service_runners:
            await runner.stop()
        self._service_runners.clear()

        # Stop API
        if self._uvicorn_ctx:
            await self._uvicorn_ctx.__aexit__(None, None, None)
            self._uvicorn_ctx = None

        # Disconnect broker
        if self._broker:
            try:
                await self._broker.__aexit__(None, None, None)
            except Exception:
                pass
            self._broker = None

        # Stop NATS if we own it
        if self._owns_nats and self.nats:
            await self.nats.__aexit__(None, None, None)
        self.nats = None

    async def _connect_remote(self) -> None:
        """Connect to remote PA."""
        # For remote PA, we just need the endpoint
        # No local components to start
        pass

    async def _wait_for_ready(self) -> None:
        """Wait for PA to be ready."""
        if not self.is_local:
            # For remote, check API health
            async with httpx.AsyncClient() as client:
                max_retries = 50
                for _ in range(max_retries):
                    try:
                        response = await client.get(
                            f"{self._endpoint}/healthcheck", timeout=1
                        )
                        if response.status_code == 200:
                            return
                    except Exception:
                        await asyncio.sleep(0.1)
                raise asyncio.TimeoutError(f"PA not ready at {self._endpoint}")

        # For local, wait for all services
        await asyncio.gather(
            *[
                runner.wait_ready(timeout=self._ready_timeout)
                for runner in self._service_runners
            ]
        )
