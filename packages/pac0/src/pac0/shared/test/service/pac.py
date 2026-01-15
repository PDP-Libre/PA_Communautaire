# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from dataclasses import dataclass
import logging
from typing import Any, AsyncContextManager, Self

import httpx
from pac0.shared.test.service.base import (
    BaseServiceContext,
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
    validation_metier: FastStreamServiceContext | None = None
    conversion_formats: FastStreamServiceContext | None = None
    annuaire_local: FastStreamServiceContext | None = None
    routage: FastStreamServiceContext | None = None
    transmission_fiscale: FastStreamServiceContext | None = None
    gestion_cycle_vie: FastStreamServiceContext | None = None

    # TODO: add all briques  ...
    client_async: httpx.AsyncClient | None = None

    def _services(self) -> list[FastApiServiceContext]:
        """returns internal services (except esb service)"""
        return (
            [
                # self.esb_central,
                self.api_gateway,
                self.controle_formats,
                self.validation_metier,
                self.conversion_formats,
                self.annuaire_local,
                self.routage,
                self.transmission_fiscale,
                self.gestion_cycle_vie,
            ]
            if self.external_url is None
            else []
        )
        # TODO: add all briques  ...
        # return []

    async def __aenter__(self) -> Self:
        """Enter the context manager (start the services if not external)"""
        # start the esb service first (api dependency)
        self.esb_central = NatsServiceContext(name="esb_central")
        await self.esb_central.__aenter__()

        # instantiate the other services (they will start later ...)
        self.api_gateway = FastApiServiceContext(nats_url=self.esb_central.url)
        self.controle_formats = FastStreamServiceContext(
            name="controle_formats",
            app_file="src/pac0/service/controle_formats/main:app",
            nats_url=self.esb_central.url,
        )
        self.validation_metier = FastStreamServiceContext(
            name="validation_metier",
            app_file="src/pac0/service/validation_metier/main:app",
            nats_url=self.esb_central.url,
        )
        self.conversion_formats = FastStreamServiceContext(
            name="conversion_formats",
            app_file="src/pac0/service/conversion_formats/main:app",
            nats_url=self.esb_central.url,
        )
        self.annuaire_local = FastStreamServiceContext(
            name="annuaire_local",
            app_file="src/pac0/service/annuaire_local/main:app",
            nats_url=self.esb_central.url,
        )
        self.routage = FastStreamServiceContext(
            name="routage",
            app_file="src/pac0/service/routage/main:app",
            nats_url=self.esb_central.url,
        )
        self.transmission_fiscale = FastStreamServiceContext(
            name="transmission_fiscale",
            app_file="src/pac0/service/transmission_fiscale/main:app",
            nats_url=self.esb_central.url,
        )
        self.gestion_cycle_vie = FastStreamServiceContext(
            name="gestion_cycle_vie",
            app_file="src/pac0/service/gestion_cycle_vie/main:app",
            nats_url=self.esb_central.url,
        )

        # start all other services
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
