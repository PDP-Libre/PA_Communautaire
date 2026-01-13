# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# see https://faststream.ag2.ai/latest/getting-started/lifespa/test/
# see https://faststream.ag2.ai/latest/getting-started/subscription/test/?h=test+nats+broker#in-memory-testing

import asyncio
import random
import socket
import threading
from contextlib import asynccontextmanager, closing
from typing import Annotated, AsyncGenerator
from unittest.mock import MagicMock, call

import faststream
import httpx
import pytest
import uvicorn
from fastapi import FastAPI
from faststream import Context, FastStream, TestApp
from faststream.context import ContextRepo
from faststream.nats import NatsBroker, TestNatsBroker
from faststream.nats.fastapi import Logger, NatsRouter
from httpx import ASGITransport, AsyncClient
from nats.server import run
from pac0.service.api_gateway.lib import router as router_api_gateway
from pac0.service.gestion_cycle_vie.lib import router as router_gestion_cycle_vie
from pac0.service.validation_metier.lib import router as router_validation_metier
from pac0.shared.tools.api import find_available_port, uvicorn_context
from pydantic import ValidationError

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


async def test_00100():
    """basic uvicorn context manager fixed port"""
    port = 8804
    async with uvicorn_context(app, port=port) as server:
        assert server.config.port == port
        base_url = f"http://0.0.0.0:{port}"

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/")
            assert response.status_code == 200
            assert response.json() == {"message": "Hello World"}


async def test_00110():
    """basic uvicorn context manager random port"""
    port = find_available_port()

    async with uvicorn_context(app, port=port) as server:
        assert server.config.port == port
        base_url = f"http://0.0.0.0:{port}"

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/")
            assert response.status_code == 200
            assert response.json() == {"message": "Hello World"}


async def test_00120():
    """basic uvicorn context manager random port 0"""
    port = 0

    async with uvicorn_context(app, port=port) as server:
        assert server.config.port != 0
        base_url = f"http://0.0.0.0:{server.config.port}"

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/")
            assert response.status_code == 200
            assert response.json() == {"message": "Hello World"}


class DeepContextManager:
    def __init__(self, app):
        self.app = app
        self._uvicorn = None
        self.uvicorn = None

    async def __aenter__(self):
        # the async context manager is NOT the same as the instance
        # we need to keep both
        self._uvicorn = uvicorn_context(app, port=0)
        self.uvicorn = await self._uvicorn.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._uvicorn.__aexit__(exc_type, exc_val, exc_tb)


async def test_00130():
    """basic uvicorn deep context manager"""
    async with DeepContextManager(app) as ctx:
        assert ctx.uvicorn.config.port != 0
        base_url = f"http://{ctx.uvicorn.config.host}:{ctx.uvicorn.config.port}"

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/")
            assert response.status_code == 200
            assert response.json() == {"message": "Hello World"}


# ===================================================================================
# a fixture with fastapi server


def _faststream_app_factory(br, router):
    app = FastStream(br)
    br.include_router(router)
    return app


routers = [
    router_validation_metier,
    router_gestion_cycle_vie,
]


class PaContext:
    """
    See https://medium.com/@hitorunajp/asynchronous-context-managers-f1c33d38c9e3
    """

    def __init__(
        self,
        # br,
        # subscriber,
        # api_app,
    ):
        self._br = None
        self.br = None
        self.subscriber = None
        # self.api_app = app_api_gateway
        self.api_base_url = None
        self._uvicorn_api = None
        self.uvicorn_api = None
        self.services_tasks = []

    async def __aenter__(self):
        # start the nats service context
        self.nats = await run(port=0)
        await self.nats.__aenter__()

        # start the broker client
        nats_url = f"nats://{self.nats.host}:{self.nats.port}"
        self._br = NatsBroker(nats_url, apply_types=True)
        self.br = await self._br.__aenter__()
        self.subscriber = self.br.subscriber("*")
        await self.br.start()

        # start the api service context
        # app_api_gateway.router = NatsRouter(nats_url)
        # app_api_gateway.router = self._br
        # app_api_gateway.include_router(app_api_gateway.router)
        app = FastAPI()
        app.state.rank = "test"

        app.state.broker = self._br
        app.include_router(router_api_gateway)

        self._uvicorn_api = uvicorn_context(app, port=0)
        self.uvicorn_api = await self._uvicorn_api.__aenter__()
        self.api_base_url = (
            f"http://{self.uvicorn_api.config.host}:{self.uvicorn_api.config.port}"
        )

        # start the services (faststream apps)
        self.services_tasks = [
            asyncio.create_task(_faststream_app_factory(self.br, router).run())
            for router in routers
        ]

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # stop the services
        # print("Stopping the services ...")
        for task in self.services_tasks:
            try:
                task.cancel()
            except asyncio.CancelledError:
                pass
        for task in self.services_tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
        # print("Services stopped")

        # close the broker client
        try:
            await self.br.__aexit__(exc_type, exc_val, exc_tb)
        except Exception:
            pass
        # close the api service context
        await self._uvicorn_api.__aexit__(exc_type, exc_val, exc_tb)
        # close the nats service context
        try:
            await self.nats.__aexit__(exc_type, exc_val, exc_tb)
        except Exception:
            pass

    def HttpxAsyncClient(self):
        return httpx.AsyncClient(base_url=self.api_base_url)

    def info(self):
        return {
            "nats_port": self.nats.port,
            "api_port": self.uvicorn_api.config.port,
        }


class MyWorldContext:
    def __init__(
        self,
        pac_pool: int,
    ):
        self.pacs: list[PaContext] = []

        assert 0 <= pac_pool <= 4

        # create pac instance
        if pac_pool >= 1:
            self.pac1 = PaContext()
            self.pacs.append(self.pac1)
        if pac_pool >= 2:
            self.pac2 = PaContext()
            self.pacs.append(self.pac2)
        if pac_pool >= 3:
            self.pac3 = PaContext()
            self.pacs.append(self.pac3)
        if pac_pool >= 4:
            self.pac4 = PaContext()
            self.pacs.append(self.pac4)

    async def __aenter__(self):
        # enter async context manager for all pac
        for pac in self.pacs:
            await pac.__aenter__()
        # TODO: how to wait for services to be ready
        await asyncio.sleep(3)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # exit async context manager for all pac
        for pac in self.pacs:
            await pac.__aexit__(exc_type, exc_val, exc_tb)


@pytest.fixture
async def my_world():
    async with MyWorldContext(pac_pool=1) as my_world:
        yield my_world


@pytest.fixture
async def my_world2():
    async with MyWorldContext(pac_pool=2) as my_world:
        yield my_world


@pytest.fixture
async def my_world3():
    async with MyWorldContext(pac_pool=3) as my_world:
        yield my_world


@pytest.fixture
async def my_world4():
    async with MyWorldContext(pac_pool=4) as my_world:
        yield my_world


@pytest.mark.asyncio
async def test_api_world_fixture(
    my_world,
) -> None:
    """
    API call on a world fixture with multiple nats/services instances
    see https://fastapi.tiangolo.com/advanced/async-tests/
    """
    async with my_world.pac1.HttpxAsyncClient() as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

        response = await client.get("/healthcheck")
        assert response.status_code == 200
        assert response.json() == {"status": "OK", "rank": "test"}


@pytest.mark.asyncio
async def test_api_world4_fixture(
    my_world4,
) -> None:
    """
    API call on a 4 pac instances world
    """
    for pac in my_world4.pacs:
        print(f"testing pac {pac} ...")

        async with pac.HttpxAsyncClient() as client:
            print(f"testing pac {pac} ...")
            print(pac.info())

            response = await client.get("/")
            assert response.status_code == 200
            assert response.json() == {"Hello": "World"}

            response = await client.get("/healthcheck")
            assert response.status_code == 200
            assert response.json() == {"status": "OK", "rank": "test"}
