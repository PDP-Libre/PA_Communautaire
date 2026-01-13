# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# see https://faststream.ag2.ai/latest/getting-started/lifespa/test/
# see https://faststream.ag2.ai/latest/getting-started/subscription/test/?h=test+nats+broker#in-memory-testing

import asyncio
from typing import Annotated
from unittest.mock import MagicMock, call

import httpx
import pytest
import uvicorn
from faststream import Context, FastStream, TestApp
from faststream.context import ContextRepo
from faststream.nats import NatsBroker, TestNatsBroker
from nats.server import run
from pac0.service.api_gateway.main import app as app_api_gateway
from pac0.service.gestion_cycle_vie.main import router as router_gestion_cycle_vie
from pac0.service.validation_metier.main import router as router_validation_metier
from pac0.shared.tools.api import find_available_port
from pydantic import ValidationError

broker = NatsBroker("nats://localhost:4222")
app = FastStream(broker, context=ContextRepo({"var1": "my-var1-value"}))
TIMEOUT = 3.0

@app.after_startup
async def handle():
    print("Calls in tests too!")


@broker.subscriber("test-subject")
async def process_test_subject(
    body: str,
    var1: Annotated[str, Context()],
):
    print("process_test_subject ...", body)
    # test some global context var
    assert var1 == "my-var1-value"


@pytest.mark.asyncio
async def test_validation_str_ok() -> None:
    """
    TestNatsBroker
    """
    async with TestNatsBroker(broker) as br:
        await br.publish("hello", subject="test-subject")
        process_test_subject.mock.assert_called_once_with("hello")


@pytest.mark.asyncio
async def test_validation_str_err() -> None:
    """
    expect str payload, get pydantic payload
    """
    async with TestNatsBroker(broker) as br:
        with pytest.raises(ValidationError):
            await br.publish({"name": "John", "user_id": 1}, subject="test-subject")


@pytest.mark.asyncio
async def test_connect_only():
    async with (
        TestNatsBroker(app.broker, connect_only=True) as br,
        TestApp(app) as test_app,
    ):
        await br.publish("hello", subject="test-subject")
        process_test_subject.mock.assert_called_once_with("hello")


@pytest.mark.asyncio
async def test_sub_embed():
    # @broker.subscriber("test-subject2")
    @broker.subscriber("*")
    async def test_process2(
        # body: str,
    ):
        # print("test_process2 ...", body)
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<< test_process2 ...")

    async with (
        TestNatsBroker(app.broker, connect_only=True) as br,
        TestApp(app) as test_app,
    ):
        await br.publish("hello2", subject="test-subject2")
        test_process2.mock.assert_called_once_with("hello2")


@pytest.fixture
async def my_test_nats_broker():
    async with (
        TestNatsBroker(app.broker, connect_only=True) as br,
        # TestApp(app) as test_app,
    ):
        yield br


@pytest.fixture
async def my_test_app():
    async with (
        # TestNatsBroker(app.broker, connect_only=True) as br,
        TestApp(app) as test_app,
    ):
        yield test_app


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.asyncio
async def test_sub_embed_fixture(my_test_nats_broker, my_test_app):
    await my_test_nats_broker.publish("hello2", subject="test-subject")
    process_test_subject.mock.assert_called_once_with("hello2")
    # TODO: how to check which subject has been called


# ===================================================================================
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.asyncio
async def test_pubsub_nats() -> None:
    """
    pub/sub on a test nats instance
    TODO: use this test to define higher-level fixtures !!
    """
    mock = MagicMock()
    queue = "q1"
    expected_messages = ("test_message_1", "test_message_2")

    async with await run(port=0) as server:
        # broker must be started !!!!
        assert server.is_running is True

        # broker = NatsBroker("nats://localhost:4222", apply_types=True)
        # broker = NatsBroker(apply_types=True)
        broker = NatsBroker(f"nats://{server.host}:{server.port}", apply_types=True)
        subscriber = broker.subscriber("*")
        # subscriber = broker.subscriber(queue)

        # async with self.patch_broker(broker) as br:
        async with broker as br:
            await br.start()

            async def publish_test_message():
                for msg in expected_messages:
                    await br.publish(msg, queue)

            async def consume():
                index_message = 0
                async for msg in subscriber:
                    result_message = await msg.decode()

                    mock(result_message)

                    index_message += 1
                    if index_message >= len(expected_messages):
                        break

            await asyncio.wait(
                (
                    asyncio.create_task(consume()),
                    asyncio.create_task(publish_test_message()),
                ),
                timeout=TIMEOUT,
            )

            calls = [call(msg) for msg in expected_messages]
            mock.assert_has_calls(calls=calls)

    # Server should be shutdown after context exit
    assert server.is_running is False


# ===================================================================================
# a basic fixture with nats server


@pytest.fixture
async def my_broker_fixture():
    async with await run(port=0) as server:
        assert server.is_running is True
        broker = NatsBroker(f"nats://{server.host}:{server.port}", apply_types=True)
        subscriber = broker.subscriber("*")
        async with broker as br:
            await br.start()
            yield br, subscriber
    assert server.is_running is False


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.asyncio
async def test_pubsub_nats_fixture(my_broker_fixture) -> None:
    """
    pub/sub on a test nats instance via basic fixture
    """
    br, subscriber = my_broker_fixture
    mock = MagicMock()
    queue = "q1"
    expected_messages = ("test_message_1", "test_message_2")

    async def publish_test_message():
        for msg in expected_messages:
            await br.publish(msg, queue)

    async def consume():
        index_message = 0
        async for msg in subscriber:
            print(msg.raw_message.subject)
            result_message = await msg.decode()

            mock(result_message)

            index_message += 1
            if index_message >= len(expected_messages):
                break

    await asyncio.wait(
        (
            asyncio.create_task(consume()),
            asyncio.create_task(publish_test_message()),
        ),
        timeout=TIMEOUT,
    )

    calls = [call(msg) for msg in expected_messages]
    mock.assert_has_calls(calls=calls)


# ===================================================================================
# a fixture with nats server, 2 faststream services and a util class
# see https://dummy.faststream.airt.ai/0.5/getting-started/integrations/frameworks/#integrations

class MyBrokerSub:
    def __init__(self, br, subscriber):
        self.br = br
        self.subscriber = subscriber


@pytest.fixture
async def my_broker_fixture_class():
    def _faststream_app_factory(router):
        app = FastStream(br)
        br.include_router(router)
        return app

    routers = [
        router_validation_metier,
        router_gestion_cycle_vie,
    ]

    async with await run(port=0) as server:
        assert server.is_running is True

        broker = NatsBroker(f"nats://{server.host}:{server.port}", apply_types=True)
        subscriber = broker.subscriber("*")
        async with broker as br:
            my_world = MyBrokerSub(br, subscriber)
            await br.start()

            services_tasks = [
                asyncio.create_task(_faststream_app_factory(router).run())
                for router in routers
            ]

            # TODO: how to wait for app to be ready
            await asyncio.sleep(3)

            yield my_world

            # Cancel the third task
            # t0.cancel()
            for task in services_tasks:
                task.cancel()
                # await t0
            for task in services_tasks:
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    assert server.is_running is False


@pytest.mark.skip("fail when running all tests")
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.asyncio
async def test_pubsub_nats_fixture_class(
    my_broker_fixture_class,
) -> None:
    """
    pub/sub on a test nats instance via a Class
    """
    br = my_broker_fixture_class.br
    subscriber = my_broker_fixture_class.subscriber

    mock = MagicMock()
    queue = "test"
    expected_messages = ("test_message_1", "test_message_2")

    async def publish_test_message():
        for msg in expected_messages:
            await br.publish(msg, queue)

    async def consume():
        index_message = 0
        async for msg in subscriber:
            print(msg.raw_message.subject)
            result_message = await msg.decode()

            mock(result_message)

            index_message += 1
            if index_message >= len(expected_messages):
                break

    # Wait for first two tasks
    await asyncio.gather(
        asyncio.create_task(consume()),
        asyncio.create_task(publish_test_message()),
        return_exceptions=True,
    )

    calls = [call(msg) for msg in expected_messages]
    mock.assert_has_calls(calls=calls)


# ===================================================================================
# a fixture with nats server, 2 faststream services and a util class
# see https://dummy.faststream.airt.ai/0.5/getting-started/integrations/frameworks/#integrations


async def run_fastapi_server(app, port):
    """
    Run FastAPI server with uvicorn in async mode.
    Automatically selects an available port.
    """
    # Configure uvicorn server
    config = uvicorn.Config(
        app,
        host="0.0.0.0",  # Listen on all interfaces
        port=port,
        log_level="info",
        # Optional: Add access logging
        access_log=True,
    )

    # Create and run server
    server = uvicorn.Server(config)
    print(f"[Server] FastAPI is running at http://localhost:{port}")
    print(f"[Server] Health check: http://localhost:{port}/health")

    # Run the server (this will block until server stops)
    try:
        await server.serve()
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        print("\n[Main] Shutdown signal received...")
        print("[Main] Stopping all tasks...")
    except Exception as e:
        # Handle unexpected errors
        print(f"[Main] Error occurred: {e}")
    finally:
        print("[Main] Application stopped")


class PaContext:
    """
    See https://medium.com/@hitorunajp/asynchronous-context-managers-f1c33d38c9e3
    """

    def __init__(self, br, subscriber):
        self.br = br
        self.subscriber = subscriber
        # async with await run(port=0) as server:

    async def __aenter__(self):
        # await self._pac1.__aenter__()
        # async with await self.nats as server:
        self.nats = await run(port=0)
        await self.nats.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # await self._pac1.__aexit__(exc_type, exc_val, exc_tb)
        try:
            await self.nats.__aexit__(exc_type, exc_val, exc_tb)
        except Exception:
            pass


class MyWorldContext:
    def __init__(self, broker, subscriber, app_api_gateway, port):
        self.broker = broker
        self.subscriber = subscriber
        self.app_api_gateway = app_api_gateway
        self.port = port

        self.pac1 = PaContext(broker, subscriber)
        # self.pac2 = PaContext(broker, subscriber)
        # self.pac3 = PaContext(broker, subscriber)
        # self.pac4 = PaContext(broker, subscriber)
        self.pacs: list[PaContext] = [self.pac1]

    async def __aenter__(self):
        await self._pac1.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self._pac1.__aexit__(exc_type, exc_val, exc_tb)
        except Exception:
            pass


@pytest.fixture
async def my_world():
    def _faststream_app_factory(router):
        app = FastStream(br)
        br.include_router(router)
        return app

    routers = [
        router_validation_metier,
        router_gestion_cycle_vie,
    ]

    async with await run(port=0) as server:
        assert server.is_running is True

        broker = NatsBroker(f"nats://{server.host}:{server.port}", apply_types=True)
        subscriber = broker.subscriber("*")

        # Find an available port
        port = find_available_port(start_port=8000)
        my_world = MyWorldContext(broker, subscriber, app_api_gateway, port)

        async with my_world.broker as br:
            await br.start()

            # start the services (faststream apps)
            services_tasks = [
                asyncio.create_task(_faststream_app_factory(router).run())
                for router in routers
            ]
            print(f"[Server] Starting FastAPI on port {port}")
            # start the api service (fastapi app)
            services_tasks.append(
                asyncio.create_task(run_fastapi_server(app_api_gateway, port))
            )

            # TODO: how to wait for services to be ready
            await asyncio.sleep(3)

            yield my_world

            # stop the services
            print("Stopping the services ...")
            for task in services_tasks:
                try:
                    task.cancel()
                except asyncio.CancelledError:
                    pass
            for task in services_tasks:
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            print("Services stopped")

    assert server.is_running is False


@pytest.mark.skip("fail when running all tests")
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.asyncio
async def test_pubsub_world_fixture(
    my_world,
) -> None:
    """
    pub/sub on a world fixture with multiple nats/services instances
    """
    br = my_world.broker
    subscriber = my_world.subscriber

    mock = MagicMock()
    queue = "test"
    expected_messages = ("test_message_1", "test_message_2")

    async def publish_test_message():
        for msg in expected_messages:
            await br.publish(msg, queue)

    async def consume():
        index_message = 0
        async for msg in subscriber:
            print(msg.raw_message.subject)
            result_message = await msg.decode()

            mock(result_message)

            index_message += 1
            if index_message >= len(expected_messages):
                break

    # Wait for first two tasks
    await asyncio.gather(
        asyncio.create_task(consume()),
        asyncio.create_task(publish_test_message()),
        return_exceptions=True,
    )

    calls = [call(msg) for msg in expected_messages]
    mock.assert_has_calls(calls=calls)


@pytest.mark.skip("fail when running all tests")
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
@pytest.mark.asyncio
async def test_api_world_fixture(
    my_world,
) -> None:
    """
    API call on a world fixture with multiple nats/services instances
    see https://fastapi.tiangolo.com/advanced/async-tests/
    """
    # br = my_world.br
    br = my_world.broker
    subscriber = my_world.subscriber

    mock = MagicMock()
    queue = "test"
    expected_messages = ("test_message_1", "test_message_2")

    base_url = f"http://0.0.0.0:{my_world.port}"
    print(f"{base_url=}")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

    async def publish_test_message():
        for msg in expected_messages:
            await br.publish(msg, queue)

    async def consume():
        index_message = 0
        async for msg in subscriber:
            print(msg.raw_message.subject)
            result_message = await msg.decode()

            mock(result_message)

            index_message += 1
            if index_message >= len(expected_messages):
                break

    # Wait for first two tasks
    await asyncio.gather(
        asyncio.create_task(consume()),
        asyncio.create_task(publish_test_message()),
        return_exceptions=True,
    )

    calls = [call(msg) for msg in expected_messages]
    mock.assert_has_calls(calls=calls)
