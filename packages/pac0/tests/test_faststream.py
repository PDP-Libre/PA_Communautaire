# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# see https://faststream.ag2.ai/latest/getting-started/lifespa/test/
# see https://faststream.ag2.ai/latest/getting-started/subscription/test/?h=test+nats+broker#in-memory-testing

import asyncio
from typing import Annotated
from unittest.mock import MagicMock, call

import pytest
from faststream import Context, FastStream, TestApp
from faststream.context import ContextRepo
from faststream.nats import NatsBroker, TestNatsBroker
from nats.server import run
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
