"""
Service Protocol definition for generic service management.

This module defines the Protocol that all services (NATS, Peppol, PA) must implement.
Services can be either:
- Local: Started as a subprocess with a command string
- Remote: Connecting to an existing endpoint (no process management)

References:
- Python Protocols: https://peps.python.org/pep-0544/
- Async Context Managers: https://docs.python.org/3/reference/datamodel.html#async-context-managers
"""

import asyncio
import subprocess
from abc import abstractmethod
from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class ServiceProtocol(Protocol):
    """
    Protocol for generic service lifecycle management.

    A service has:
    - An endpoint URL (http://, nats://, etc.)
    - An optional subprocess (for locally managed services)
    - Context manager behavior for clean start/stop

    Examples:
        # Local service with subprocess
        async with NatsService(command="nats-server -p 4222") as svc:
            print(svc.endpoint)  # nats://localhost:4222

        # Remote service (no subprocess)
        async with NatsService(endpoint="nats://ebs.dev.paxpar.tech") as svc:
            print(svc.endpoint)  # nats://ebs.dev.paxpar.tech
    """

    @property
    def endpoint(self) -> str:
        """
        The service endpoint URL.

        Format depends on service type:
        - NATS: nats://host:port
        - HTTP: http://host:port or https://host:port
        - Custom protocols as needed

        Returns:
            str: The endpoint URL
        """
        ...

    @property
    def process(self) -> Optional[subprocess.Popen]:
        """
        The subprocess handle for locally managed services.

        Returns:
            Optional[subprocess.Popen]: The subprocess if local, None if remote
        """
        ...

    @property
    def is_local(self) -> bool:
        """
        Whether this service is locally managed (has a subprocess).

        Returns:
            bool: True if local (subprocess managed), False if remote
        """
        ...

    @property
    def is_running(self) -> bool:
        """
        Whether the service is currently running.

        Returns:
            bool: True if the service is running and accessible
        """
        ...

    async def wait_ready(self, timeout: float = 10.0) -> None:
        """
        Wait for the service to be ready.

        Args:
            timeout: Maximum time to wait in seconds

        Raises:
            asyncio.TimeoutError: If service doesn't become ready within timeout
        """
        ...

    async def __aenter__(self) -> "ServiceProtocol":
        """Enter the async context manager, starting the service if local."""
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager, stopping the service if local."""
        ...


class BaseService:
    """
    Base class providing common service functionality.

    Subclasses must implement:
    - _start_local(): Start the local subprocess
    - _stop_local(): Stop the local subprocess
    - _check_ready(): Check if service is ready
    - _connect_remote(): Connect to remote service

    Attributes:
        _endpoint: The service endpoint URL
        _command: Command string for local subprocess
        _process: The subprocess handle (if local)
        _ready: Event signaling service readiness
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        command: Optional[str] = None,
    ):
        """
        Initialize a service.

        Args:
            endpoint: Remote endpoint URL (mutually exclusive with command)
            command: Command string to start local service (mutually exclusive with endpoint)

        Raises:
            ValueError: If neither or both endpoint and command are provided
        """
        if endpoint and command:
            raise ValueError("Cannot specify both endpoint and command")

        self._endpoint: str = endpoint or ""
        self._command: Optional[str] = command
        self._process: Optional[subprocess.Popen] = None
        self._ready = asyncio.Event()
        self._running = False

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @property
    def process(self) -> Optional[subprocess.Popen]:
        return self._process

    @property
    def is_local(self) -> bool:
        return self._command is not None

    @property
    def is_running(self) -> bool:
        return self._running

    async def wait_ready(self, timeout: float = 10.0) -> None:
        """Wait for service readiness with timeout."""
        await asyncio.wait_for(self._ready.wait(), timeout=timeout)

    async def __aenter__(self) -> "BaseService":
        if self.is_local:
            await self._start_local()
        else:
            await self._connect_remote()

        # Wait for readiness
        await self._wait_for_ready()
        self._running = True
        self._ready.set()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._running = False
        self._ready.clear()

        if self.is_local:
            await self._stop_local()
        else:
            await self._disconnect_remote()

    # Abstract methods for subclasses
    async def _start_local(self) -> None:
        """Start the local subprocess. Must be implemented by subclasses."""
        raise NotImplementedError

    async def _stop_local(self) -> None:
        """Stop the local subprocess. Must be implemented by subclasses."""
        raise NotImplementedError

    async def _connect_remote(self) -> None:
        """Connect to remote service. Must be implemented by subclasses."""
        raise NotImplementedError

    async def _disconnect_remote(self) -> None:
        """Disconnect from remote service. Default implementation does nothing."""
        pass

    async def _wait_for_ready(self) -> None:
        """Wait for service to be ready. Must be implemented by subclasses."""
        raise NotImplementedError
