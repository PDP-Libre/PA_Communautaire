import asyncio
from dataclasses import dataclass
import logging
from typing import Any, AsyncContextManager, Self

import httpx
from pac0.shared.test.service.base import (
    BaseServiceContext,
    ServiceConfig,
)
from pac0.shared.test.service.fastapi import FastApiServiceContext
from pac0.shared.test.service.faststream import FastStreamServiceContext
from pac0.shared.test.service.nats import NatsServiceContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PacServiceContext(BaseServiceContext):
    """Test context for a PA service."""

    external_url: str | None = None
    api_gateway: FastApiServiceContext | None = None
    esb_central: NatsServiceContext | None = None
    controle_formats: FastStreamServiceContext | None = None
    # TODO: add all briques  ...
    client_async: httpx.AsyncClient | None = None

    def _services(self) -> list[AsyncContextManager]:
        """returns internal services"""
        return (
            [
                self.api_gateway,
                self.esb_central,
                self.controle_formats,
            ]
            if self.external_url is None
            else []
        )
        # TODO: add all briques  ...
        # return []

    async def __aenter__(self) -> Self:
        """Enter the context manager (start the services if not external)"""
        self.api_gateway = FastApiServiceContext(name="api_gateway")
        self.esb_central = NatsServiceContext(name="esb_central")
        self.controle_formats = FastStreamServiceContext(
            name="controle_formats",
            app_file="src/pac0/service/validation_metier/main:app",
        )

        await asyncio.gather(*[s.__aenter__() for s in self._services()])

        # starts an async client
        self.client_async = await self.api_gateway.get_client_async().__aenter__()

        # logger.info(f"Service started on {self.config.host}:{self.config.port}")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context manager (stop the services if not external)"""
        # exit the async client
        if self.client_async:
            await self.client_async.__aexit__(exc_type, exc_val, exc_tb)
            self.client_async = None
        # exit the internal services
        await asyncio.gather(
            *[s.__aexit__(exc_type, exc_val, exc_tb) for s in self._services()]
        )
