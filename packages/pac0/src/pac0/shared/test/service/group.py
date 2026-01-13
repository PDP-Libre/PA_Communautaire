# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncGenerator, Generator, Self
import asyncio

import httpx
from pac0.shared.test.service.base import (
    BaseServiceContext,
    ServiceConfig,
)


class FastStreamServiceContext(BaseServiceContext):
    """Test context for a DNS service."""

    def __init__(self, configs: list[ServiceConfig]) -> None:
        self.configs = configs
        self.services = [BaseServiceContext(config) for config in configs]

    async def __aenter__(self) -> Self:
        await asyncio.gather([s.__aenter__() for s in self.services])
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await asyncio.gather(
            [s.__aexit__(exc_type, exc_val, exc_tb) for s in self.services]
        )

    async def _terminate(self) -> None:
        """Terminate all the subprocesses."""
        await asyncio.gather([s._terminate() for s in self.services])

    async def wait_for_ready(self, timeout: float = 30.0) -> bool:
        """Wait for services to be ready via TCP and HTTP health check."""
        tasks = [service.wait_for_ready(timeout) for service in self.services]
        results = await asyncio.gather(*tasks)
        return all(results)

    @contextmanager
    def get_client(self) -> Generator[httpx.Client, None, None]:
        raise NotImplementedError("Can't get a client on a service group !")

    @asynccontextmanager
    async def get_client_async(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        raise NotImplementedError("Can't get a client on a service group !")
