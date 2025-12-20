import asyncio
from nats.server import run
# inspired by  https://github.com/nats-io/nats.py/blob/main/nats-server/tests/test_server.py


async def test_nats():
    """NATS with dynamic port"""
    server = await run(port=0)

    assert server.port > 0
    assert server.host == "0.0.0.0"
    assert server.is_running is True

    await server.shutdown()
    assert server.is_running is False


async def test_nats_context_manager():
    """NATS as context manager"""
    async with await run(port=0) as server:
        assert server.is_running is True
        assert server.port > 0

    # Server should be shutdown after context exit
    assert server.is_running is False
