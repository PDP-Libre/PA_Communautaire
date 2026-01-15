# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
TODO:
* [ ] create class ServiceGroupContext
* [ ] create pytest test suite in packages/pac0/src/pac0/tests/shared/test/test_service.py
* [ ] create pytest fixture
* add tests functions


prompt:

Complete code in @packages/pac0/src/pac0/shared/test/service.py by following instructions and TODO
in docstring and comment.

"""

from abc import abstractmethod
import asyncio
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
import logging
import os
from pathlib import Path
import socket
import subprocess
import time
from typing import Any, AsyncGenerator, Generator, Protocol, Self, runtime_checkable

import httpx

from pac0.shared.tools.api import find_available_port


logger = logging.getLogger(__name__)

PACKAGE_BASE_FOLDER = (
    Path(__file__)
    .absolute()
    # /home/.../packages/pac0/src/pac0/shared/test/service/base.py
    .parent
    # /home/.../packages/pac0/src/pac0/shared/test/service \
    .parent
    # /home/.../packages/pac0/src/pac0/shared/test
    .parent
    # /home/.../packages/pac0/src/pac0/shared
    .parent
    # /home/.../packages/pac0/src/pac0
    .parent
    # /home/.../packages/pac0/src
    .parent
    # /home/.../packages/pac0
)


@runtime_checkable
class ServiceContext(Protocol):
    """
    Protocol defining interface for service lifecycle management.
    Using typing.Protocol provides better type checking and interface definition.
    """

    @abstractmethod
    async def __aenter__(self) -> Self:
        """Async context manager entry - starts the service."""
        ...

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit - stops the service."""
        ...

    @abstractmethod
    async def wait_for_ready(self, timeout: float = 30.0) -> bool:
        """Wait for service to be ready via health check."""
        ...

    @abstractmethod
    @contextmanager
    def get_client(self) -> Generator[Any, None, None]:
        """Sync context manager for service client."""
        ...

    @abstractmethod
    @asynccontextmanager
    async def get_client_async(self) -> AsyncGenerator[Any, None]:
        """Async context manager for service client."""
        ...


@dataclass
class ServiceConfig:
    """Configuration for a service."""

    command: list[str]
    name: str = "unknown"
    host: str = "localhost"
    port: int = 8000
    health_check_path: str | None = "/health"
    health_check_timeout: float = 5.0
    startup_timeout: float = 30.0
    shutdown_timeout: float = 10.0
    allow_ConnectionRefusedError: bool = False
    stdout: int = subprocess.PIPE
    stderr: int = subprocess.PIPE
    env_var_extra: dict[str, str] | None = None



# TODO: move to BaseModel
class BaseServiceContext:
    """
    Base implementation of ServiceContext protocol.
    Using composition over inheritance for better flexibility.
    """

    def __init__(self, config: ServiceConfig) -> None:
        self.config = config
        self._process: subprocess.Popen | None = None
        self._client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None
        self.is_ready = False

    # Explicitly declare that this class implements ServiceContext protocol
    def __init_subclass__(cls) -> None:
        """Ensure subclasses properly implement the ServiceContext protocol."""
        if not isinstance(cls, ServiceContext):
            raise TypeError(f"{cls.__name__} must implement ServiceContext protocol")

    async def __aenter__(self) -> Self:
        """Start the service subprocess."""
        if self.config.port == 0:
            self.config.port = await find_available_port()
        logger.info(
            f"Starting service {self.config.name} on port {self.config.port} : {' '.join(self.config.command)}"
        )
        env = os.environ.copy()
        env["PORT"] = str(self.config.port)
        if self.config.env_var_extra:
            env.update(self.config.env_var_extra)
        command = [c.format(**env) for c in self.config.command]

        self._process = subprocess.Popen(
            command,
            # TODO: BUG, break if uncommented !
            # stdout=subprocess.PIPE,  # self.config.stdout,
            # stderr=subprocess.PIPE,  # self.config.stderr,
            text=True,
            env=env,
            cwd=PACKAGE_BASE_FOLDER,
        )

        # Wait for service to be ready
        self.is_ready = await self.wait_for_ready(self.config.startup_timeout)
        if not self.is_ready:
            await self._terminate()
            raise TimeoutError(
                f"Service {self.config.name} failed to start within {self.config.startup_timeout}s"
            )

        logger.info(
            f"Service  {self.config.name} started on {self.config.host}:{self.config.port}"
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop the service subprocess."""
        await self._terminate()

    async def _terminate(self) -> None:
        """Terminate the subprocess."""
        if self._process:
            logger.info("Stopping service...")
            self._process.terminate()

            try:
                self._process.wait(timeout=self.config.shutdown_timeout)
            except subprocess.TimeoutExpired:
                logger.warning("Service didn't terminate gracefully, killing...")
                self._process.kill()
                self._process.wait()

            self._process = None

    async def wait_for_ready(self, timeout: float = 30.0) -> bool:
        """Wait for service to be ready via TCP and HTTP health check."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            logger.debug(f"wait_for_ready {self.config.name} ...")
            # First check TCP connectivity
            if self._check_tcp_connectivity():
                # Then check HTTP health endpoint if applicable
                if self.config.health_check_path is None:
                    return True
                elif await self._check_http_health():
                    return True

            await asyncio.sleep(1.0)

        return False

    def _check_tcp_connectivity(
        self,
    ) -> bool:
        """Check if we can connect to the service via TCP."""
        #print("tcp ...", self.config.host, self.config.port)

        try:
            sock = socket.create_connection(
                (self.config.host, self.config.port), timeout=1.0
            )
            sock.close()
            return True
        except ConnectionRefusedError:
            return self.config.allow_ConnectionRefusedError
        except (socket.timeout, OSError) as e:
            # print(e)
            return False
        

    async def _check_http_health(self) -> bool:
        """Check HTTP health endpoint."""
        try:
            url = f"http://{self.config.host}:{self.config.port}{self.config.health_check_path}"
            print("_check_http_health", url)
            async with httpx.AsyncClient(
                timeout=self.config.health_check_timeout
            ) as client:
                response = await client.get(
                    url
                )
                return response.status_code == 200
        except Exception as e:
            print("cccccc", e)
            return False

    @contextmanager
    def get_client(self) -> Generator[httpx.Client, None, None]:
        """Get a synchronous HTTP client."""
        client = httpx.Client(
            base_url=f"http://{self.config.host}:{self.config.port}",
            timeout=self.config.health_check_timeout,
        )
        try:
            yield client
        finally:
            client.close()

    @asynccontextmanager
    async def get_client_async(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Get an asynchronous HTTP client."""
        async with httpx.AsyncClient(
            base_url=f"http://{self.config.host}:{self.config.port}",
            timeout=self.config.health_check_timeout,
        ) as client:
            yield client

    @property
    def url(self) -> str:
        # TODO: add self.protocol to avoid overridding
        return f"http://{self.config.host}:{self.config.port}"
