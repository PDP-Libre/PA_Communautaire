"""
Progressive service lifecycle tests.

Tests are ordered from simplest to most complex:
1. NATS server lifecycle
2. NATS context manager pattern
3. Broker connection
4. Pub/sub messaging
5. Single FastStream service
6. Multiple FastStream services
7. FastAPI + services integration
8. Full PA context
9. Multi-PA pool
10. Cross-PA communication

References:
- FastStream Testing: https://faststream.ag2.ai/latest/getting-started/lifespan/test/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
- NATS Python: https://github.com/nats-io/nats.py
"""

import asyncio
from unittest.mock import MagicMock, call

import pytest
from faststream.nats import NatsBroker, NatsRouter
from nats.server import run as nats_run
from pac0.service.gestion_cycle_vie.lib import router as router_gestion_cycle_vie
from pac0.service.validation_metier.lib import router as router_validation_metier
from pac0.shared.test.service_fixture import (
    BrokerContext,
    NatsServerContext,
    PaServiceContext,
    ServicePoolContext,
    ServiceRunner,
    WorldServiceContext,
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


# ============================================================================
# Level 5-6: FastStream Services
# ============================================================================


class TestFastStreamServices:
    """
    Test FastStream service lifecycle with readiness detection.

    See: https://faststream.ag2.ai/latest/getting-started/lifespan/hooks/
    """

    async def test_05_single_service_with_readiness(self, nats_server):
        """
        Level 5: Single FastStream service with @app.after_startup readiness.

        Demonstrates the ServiceRunner pattern that replaces sleep(3).
        """
        async with BrokerContext(nats_server.url) as ctx:
            # Create a simple test router
            test_router = NatsRouter()
            received = []

            @test_router.subscriber("test-in")
            async def handler(msg: str):
                received.append(msg)

            # Use ServiceRunner with readiness detection
            runner = ServiceRunner(ctx.broker, test_router, name="test-service")

            task = await runner.start()

            # Wait for service to be ready (uses @app.after_startup)
            await runner.wait_ready(timeout=5.0)

            # Service is now ready - send a message
            await ctx.broker.publish("hello", "test-in")

            # Give time for message processing
            await asyncio.sleep(0.5)
            assert len(received) == 1, "single message recieved"
            
            await runner.stop()

            assert runner.ready.is_set(), "Service should have signaled ready"

    async def test_05b_service_readiness_timeout(self, nats_server):
        """
        Level 5b: Verify timeout behavior for service readiness.
        """
        async with BrokerContext(nats_server.url) as ctx:
            test_router = NatsRouter()

            @test_router.subscriber("dummy")
            async def handler(msg: str):
                pass

            runner = ServiceRunner(ctx.broker, test_router, name="test")

            # Don't start the service - readiness should timeout
            with pytest.raises(asyncio.TimeoutError):
                await runner.wait_ready(timeout=0.1)

    async def test_06_multiple_services_pool(self, nats_server):
        """
        Level 6: Multiple FastStream services started together.

        Uses ServicePoolContext for coordinated startup.
        """
        async with BrokerContext(nats_server.url) as ctx:
            # Create two test routers
            router1 = NatsRouter()
            router2 = NatsRouter()

            @router1.subscriber("service1-in")
            async def handler1(msg: str):
                pass

            @router2.subscriber("service2-in")
            async def handler2(msg: str):
                pass

            routers = [
                (router1, "service1"),
                (router2, "service2"),
            ]

            async with ServicePoolContext(
                ctx.broker, routers, ready_timeout=5.0
            ) as pool:
                assert len(pool.runners) == 2
                assert all(r.ready.is_set() for r in pool.runners)

    async def test_06b_real_services_pool(self, nats_server):
        """
        Level 6b: Real application services (validation, gestion).
        """
        async with BrokerContext(nats_server.url) as ctx:
            routers = [
                (router_validation_metier, "validation-metier"),
                (router_gestion_cycle_vie, "gestion-cycle-vie"),
            ]

            async with ServicePoolContext(
                ctx.broker, routers, ready_timeout=10.0
            ) as pool:
                assert len(pool.runners) == 2

                for runner in pool.runners:
                    assert runner.ready.is_set(), f"{runner.name} should be ready"


# ============================================================================
# Level 7-8: Full Integration
# ============================================================================


class TestFullIntegration:
    """
    Test complete PA integration with FastAPI + NATS + FastStream.

    See: https://fastapi.tiangolo.com/advanced/async-tests/
    """

    async def test_07_fastapi_with_services(self, pa_service):
        """
        Level 7: FastAPI gateway with connected services.
        """
        async with pa_service.http_client() as client:
            # Test root endpoint
            response = await client.get("/")
            assert response.status_code == 200
            assert response.json() == {"Hello": "World"}

    async def test_07b_healthcheck_with_services(self, pa_service):
        """
        Level 7b: Healthcheck endpoint publishes to NATS.
        """
        async with pa_service.http_client() as client:
            response = await client.get("/healthcheck")
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "OK"
            assert data["rank"] == "test"

    async def test_08_full_pa_context(self, pa_service):
        """
        Level 8: Full PaServiceContext verification.
        """
        # Verify all components are running
        assert pa_service.nats.is_running, "NATS should be running"
        assert pa_service.broker is not None, "Broker should be connected"
        assert pa_service.api_base_url, "API URL should be set"

        # Verify info() helper
        info = pa_service.info()
        assert info["nats_port"] > 0
        assert info["api_port"] > 0
        assert (
            "localhost" in info["api_base_url"] or "127.0.0.1" in info["api_base_url"]
        )

    async def test_08b_pa_context_isolation(self):
        """
        Level 8b: Each PA context is isolated.
        """
        async with PaServiceContext() as pa1:
            async with PaServiceContext() as pa2:
                # Different NATS ports
                assert pa1.nats.port != pa2.nats.port

                # Different API ports
                assert pa1.uvicorn_server.config.port != pa2.uvicorn_server.config.port


# ============================================================================
# Level 9-10: Multi-PA Pool
# ============================================================================


class TestMultiPaPool:
    """
    Test multiple PA instances for multi-platform scenarios.
    """

    async def test_09_multi_pa_pool_2pa(self, world_service_2pa):
        """
        Level 9: World with 2 PA instances.
        """
        assert len(world_service_2pa.pacs) == 2
        assert world_service_2pa.pac1 is not None
        assert world_service_2pa.pac2 is not None

        # Verify isolation
        assert world_service_2pa.pac1.nats.port != world_service_2pa.pac2.nats.port

        # Verify both are functional
        for pac in world_service_2pa.pacs:
            async with pac.http_client() as client:
                response = await client.get("/healthcheck")
                assert response.status_code == 200

    async def test_09b_multi_pa_pool_4pa(self):
        """
        Level 9b: World with maximum 4 PA instances.
        """
        async with WorldServiceContext(pac_count=4) as world:
            assert len(world.pacs) == 4

            ports = [pac.nats.port for pac in world.pacs]
            assert len(set(ports)) == 4, "All NATS ports should be unique"

            api_ports = [pac.uvicorn_server.config.port for pac in world.pacs]
            assert len(set(api_ports)) == 4, "All API ports should be unique"

    async def test_10_cross_pa_info(self, world_service_2pa):
        """
        Level 10: Verify PA instances have independent info.

        Note: Cross-PA message routing would require additional
        infrastructure (central directory, federation) not yet implemented.
        """
        info1 = world_service_2pa.pac1.info()
        info2 = world_service_2pa.pac2.info()

        # Print for debugging
        print(f"PA1: {info1}")
        print(f"PA2: {info2}")

        # Verify independence
        assert info1["nats_port"] != info2["nats_port"]
        assert info1["api_port"] != info2["api_port"]
        assert info1["nats_url"] != info2["nats_url"]
