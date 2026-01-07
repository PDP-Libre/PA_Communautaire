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
from httpx import ASGITransport, AsyncClient
from nats.server import run
from pac0.service.api_gateway.main import app as app_api_gateway
from pac0.service.gestion_cycle_vie.main import router as router_gestion_cycle_vie
from pac0.service.validation_metier.main import router as router_validation_metier
from pac0.shared.tools.api import find_available_port
from pydantic import ValidationError

from pac0.shared.tools.api import uvicorn_context

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
        api_app,
    ):
        self.br = None
        self.subscriber = None
        self.api_app = api_app
        self.api_base_url = None
        self._uvicorn_api = None
        self.uvicorn_api = None
        self.services_tasks = []

    async def __aenter__(self):
        # start the nats service context
        self.nats = await run(port=0)
        await self.nats.__aenter__()
        broker = NatsBroker(
            f"nats://{self.nats.host}:{self.nats.port}", apply_types=True
        )
        self.br = broker
        self.subscriber = broker.subscriber("*")

        # start the api service context
        self._uvicorn_api = uvicorn_context(self.api_app, port=0)
        self.uvicorn_api = await self._uvicorn_api.__aenter__()
        self.api_base_url = (
            f"http://{self.uvicorn_api.config.host}:{self.uvicorn_api.config.port}"
        )
        print(f"{self.api_base_url=}")
        # start the broker client
        await self.br.__aenter__()
        await self.br.start()

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
        await self.br.__aexit__(exc_type, exc_val, exc_tb)
        # close the api service context
        await self._uvicorn_api.__aexit__(exc_type, exc_val, exc_tb)
        # close the nats service context
        await self.nats.__aexit__(exc_type, exc_val, exc_tb)

    def HttpxAsyncClient(self):
        return httpx.AsyncClient(base_url=self.api_base_url)


class WorldContext:
    def __init__(
        self,
        # broker,
        # subscriber,
        # app_api_gateway,
        pac_pool: int,
    ):
        # self.broker = broker
        # self.subscriber = subscriber
        self.pacs: list[PaContext] = []

        assert 0 <= pac_pool <= 4

        # create pac instance
        if pac_pool >= 1:
            self.pac1 = PaContext(app_api_gateway)
            self.pacs.append(self.pac1)
        if pac_pool >= 2:
            self.pac2 = PaContext(app_api_gateway)
            self.pacs.append(self.pac2)
        if pac_pool >= 3:
            self.pac3 = PaContext(app_api_gateway)
            self.pacs.append(self.pac3)
        if pac_pool >= 4:
            self.pac4 = PaContext(app_api_gateway)
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
    async with WorldContext(pac_pool=1) as my_world:
        yield my_world


@pytest.fixture
async def my_world2():
    async with WorldContext(pac_pool=2) as my_world:
        yield my_world


@pytest.fixture
async def my_world3():
    async with WorldContext(pac_pool=3) as my_world:
        yield my_world


@pytest.fixture
async def my_world4():
    async with WorldContext(pac_pool=4) as my_world:
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
        assert response.json() == {"status": "OK"}


@pytest.mark.asyncio
async def test_api_world4_fixture(
    my_world4,
) -> None:
    """
    API call on a 4 pac instances world
    """
    print("xxxxxxxxxxxxx")
    for pac in my_world4.pacs:
        print(f"testing pac {pac} ...")

        async with pac.HttpxAsyncClient() as client:
            print(f"testing pac {pac} ...")

            response = await client.get("/")
            assert response.status_code == 200
            assert response.json() == {"Hello": "World"}

            response = await client.get("/healthcheck")
            assert response.status_code == 200
            assert response.json() == {"status": "OK"}
