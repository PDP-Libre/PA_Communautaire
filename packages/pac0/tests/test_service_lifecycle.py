# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# TODO: review those tests thay may be obsolete

import asyncio
from unittest.mock import MagicMock, call

from faststream.nats import NatsBroker
from nats.server import run as nats_run
from pac0.shared.test.service_fixture import (
    BrokerContext,
    NatsServerContext,
)

# ============================================================================
# Level 1-2: NATS Server Lifecycle
# ============================================================================


class TestNatsServerLifecycle:
    """
    Test NATS server start/stop patterns.

    See: https://github.com/nats-io/nats.py/tree/main/nats-server
    """

    async def test_01_nats_server_manual_lifecycle(self):
        """
        Level 1: Manual NATS server start/stop.

        Demonstrates the basic pattern without context managers.
        """
        # Start server with dynamic port
        server = await nats_run(port=0)

        try:
            assert server.port > 0, "Server should have a dynamic port"
            assert server.host == "0.0.0.0", "Server should bind to all interfaces"
            assert server.is_running is True, "Server should be running"
        finally:
            await server.shutdown()

        assert server.is_running is False, "Server should be stopped"

    async def test_02_nats_server_context_manager(self):
        """
        Level 2: NATS server as async context manager.

        Preferred pattern for tests - automatic cleanup.
        """
        async with await nats_run(port=0) as server:
            assert server.is_running is True
            assert server.port > 0

        # Server should be stopped after context exit
        assert server.is_running is False

    async def test_02b_nats_server_context_wrapper(self):
        """
        Level 2b: Using NatsServerContext wrapper class.

        Provides additional conveniences like .url property.
        """
        async with NatsServerContext() as ctx:
            assert ctx.is_running is True
            assert ctx.port > 0
            assert ctx.url.startswith("nats://")
            assert str(ctx.port) in ctx.url


# ============================================================================
# Level 3-4: Broker Connection and Messaging
# ============================================================================


class TestBrokerConnection:
    """
    Test NatsBroker connection and basic messaging.

    See: https://faststream.ag2.ai/latest/nats/
    """

    async def test_03_broker_connection(self, nats_server):
        """
        Level 3: Connect NatsBroker to NATS server.
        """
        broker = NatsBroker(nats_server.url, apply_types=True)

        async with broker as br:
            await br.start()
            # Broker is connected if no exception raised
            assert br is not None

    async def test_03b_broker_context_wrapper(self, nats_server):
        """
        Level 3b: Using BrokerContext wrapper class.
        """
        async with BrokerContext(nats_server.url) as ctx:
            assert ctx.broker is not None
            assert ctx.wildcard_subscriber is not None

    async def test_04_broker_pubsub_basic(self, nats_server):
        """
        Level 4: Basic publish/subscribe with mock verification.
        """
        mock = MagicMock()
        messages_to_send = ["message_1", "message_2"]

        broker = NatsBroker(nats_server.url, apply_types=True)
        subscriber = broker.subscriber("test-subject")

        async with broker as br:
            await br.start()

            async def consume():
                count = 0
                async for msg in subscriber:
                    decoded = await msg.decode()
                    mock(decoded)
                    count += 1
                    if count >= len(messages_to_send):
                        break

            async def publish():
                for msg in messages_to_send:
                    await br.publish(msg, "test-subject")

            # Run both concurrently with timeout
            await asyncio.wait_for(asyncio.gather(consume(), publish()), timeout=5.0)

        # Verify all messages received
        mock.assert_has_calls([call(m) for m in messages_to_send])

    async def test_04b_broker_pubsub_wildcard(self, broker_context):
        """
        Level 4b: Wildcard subscriber receives from any subject.
        """
        mock = MagicMock()

        async def consume():
            async for msg in broker_context.wildcard_subscriber:
                decoded = await msg.decode()
                mock(decoded, msg.raw_message.subject)
                break  # Just capture one

        async def publish():
            await broker_context.broker.publish("test-data", "any.subject.here")

        await asyncio.wait_for(asyncio.gather(consume(), publish()), timeout=5.0)

        mock.assert_called_once()

