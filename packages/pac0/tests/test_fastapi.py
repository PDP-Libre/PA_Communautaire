# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# see https://faststream.ag2.ai/latest/getting-started/lifespa/test/
# see https://faststream.ag2.ai/latest/getting-started/subscription/test/?h=test+nats+broker#in-memory-testing

import httpx
from fastapi import FastAPI
from pac0.shared.tools.api import find_available_port, uvicorn_context


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

