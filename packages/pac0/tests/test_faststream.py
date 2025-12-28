import pytest
import faststream
from faststream import FastStream, TestApp
from faststream.nats import NatsBroker, TestNatsBroker
from pydantic import ValidationError

broker = NatsBroker("nats://localhost:4222")
app = FastStream(broker)


@pytest.mark.asyncio
async def test_TestNatsBroker() -> None:
    """
    TestNatsBroker
    see https://faststream.ag2.ai/latest/getting-started/subscription/test/?h=test+nats+broker#in-memory-testing
    """
    async with TestNatsBroker(broker) as br:
        await br.publish({"name": "John", "user_id": 1}, subject="test-subject")

