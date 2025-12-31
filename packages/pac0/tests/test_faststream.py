# see https://faststream.ag2.ai/latest/getting-started/lifespa/test/
# see https://faststream.ag2.ai/latest/getting-started/subscription/test/?h=test+nats+broker#in-memory-testing

from typing import Annotated
import pytest
import faststream
from faststream.context import ContextRepo
from faststream import FastStream, TestApp, Context
from faststream.nats import NatsBroker, TestNatsBroker
from pydantic import ValidationError

broker = NatsBroker("nats://localhost:4222")
app = FastStream(broker, context=ContextRepo({"var1": "my-var1-value"}))


@app.after_startup
async def handle():
    print("Calls in tests too!")


@broker.subscriber("test-subject")
async def test_process(
    body: str,
    var1: Annotated[str, Context()],
):
    print("test_process ...", body)
    # test some global context var
    assert var1 == "my-var1-value"


@pytest.mark.asyncio
async def test_validation_str_ok() -> None:
    """
    TestNatsBroker
    """
    async with TestNatsBroker(broker) as br:
        await br.publish("hello", subject="test-subject")
        test_process.mock.assert_called_once_with("hello")


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
        test_process.mock.assert_called_once_with("hello")


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

    assert False