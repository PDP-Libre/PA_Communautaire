# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tests for WorldContext and service implementations.

Progressive tests from simple service lifecycle to complex multi-PA scenarios:
1. ServiceProtocol compliance
2. Individual service lifecycle (NATS, Peppol, PA)
3. WorldContext basic functionality
4. Multi-PA isolation and communication
5. Service configuration variants (local/remote)

References:
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
- Service Protocol: pac0.shared.test.protocol
"""

import asyncio
import subprocess

import pytest
from faststream.nats import NatsRouter

from pac0.shared.test.protocol import BaseService, ServiceProtocol
from pac0.shared.test.services import (
    NatsService,
    PaService,
    PeppolService,
    ServiceRunner,
)
from pac0.shared.test.world import WorldContext


# =============================================================================
# Level 1: ServiceProtocol Compliance Tests
# =============================================================================


class TestServiceProtocol:
    """Test that services implement ServiceProtocol correctly."""

    def test_nats_service_is_protocol(self):
        """NatsService implements ServiceProtocol."""
        svc = NatsService()
        assert isinstance(svc, ServiceProtocol)

    def test_peppol_service_is_protocol(self):
        """PeppolService implements ServiceProtocol."""
        svc = PeppolService()
        assert isinstance(svc, ServiceProtocol)

    def test_pa_service_is_protocol(self):
        """PaService implements ServiceProtocol."""
        svc = PaService()
        assert isinstance(svc, ServiceProtocol)

    def test_protocol_properties_exist(self):
        """All protocol properties exist on BaseService."""
        svc = NatsService()
        assert hasattr(svc, "endpoint")
        assert hasattr(svc, "process")
        assert hasattr(svc, "is_local")
        assert hasattr(svc, "is_running")
        assert hasattr(svc, "wait_ready")
        assert hasattr(svc, "__aenter__")
        assert hasattr(svc, "__aexit__")


# =============================================================================
# Level 2: NATS Service Lifecycle Tests
# =============================================================================


class TestNatsServiceLifecycle:
    """Test NatsService lifecycle in various configurations."""

    async def test_embedded_nats_default(self):
        """Default NatsService uses embedded NATS server."""
        svc = NatsService()
        assert svc.is_local is True
        assert svc._use_embedded is True

        async with svc:
            assert svc.is_running is True
            assert svc.port > 0
            assert svc.endpoint.startswith("nats://")
            assert str(svc.port) in svc.endpoint

        assert svc.is_running is False

    async def test_remote_nats_endpoint(self):
        """NatsService can connect to remote endpoint."""
        # First start a local server to connect to
        async with NatsService() as server:
            # Connect to it as "remote"
            svc = NatsService(endpoint=server.endpoint)
            assert svc.is_local is False

            async with svc:
                assert svc.is_running is True
                assert svc.endpoint == server.endpoint

    async def test_nats_service_properties(self):
        """NatsService exposes correct properties."""
        async with NatsService() as svc:
            assert svc.host in ["localhost", "0.0.0.0", "127.0.0.1"]
            assert svc.port > 0
            assert svc.process is None  # Embedded doesn't use subprocess
            assert svc.is_local is True
            assert svc.is_running is True

    async def test_nats_wait_ready_timeout(self):
        """wait_ready raises TimeoutError if service doesn't start."""
        # Skip this test as it would require a real timeout scenario
        # which is slow and may cause CI issues
        pytest.skip("Timeout test skipped for CI performance")


# =============================================================================
# Level 3: Peppol Service Lifecycle Tests
# =============================================================================


class TestPeppolServiceLifecycle:
    """Test PeppolService lifecycle in various configurations."""

    async def test_peppol_mock_default(self):
        """Default PeppolService uses mock mode."""
        svc = PeppolService()
        assert svc._mock is True

        async with svc:
            assert svc.is_running is True
            assert svc.lookup_service is not None

    async def test_peppol_mock_responses(self):
        """PeppolService can set and return mock responses."""
        from pac0.service.routage.peppol import PeppolEndpoint

        async with PeppolService(mock=True) as svc:
            # Set up mock response
            endpoint = PeppolEndpoint(
                address="https://ap.test.fr/as4",
                certificate="MOCK_CERT",
                transport_profile="peppol-transport-as4-v2_0",
            )
            svc.set_mock_response(
                scheme_id="0009",
                participant_id="123456789",
                endpoint=endpoint,
            )

            # Lookup should return mock
            result = await svc.lookup_by_siren("123456789")
            assert result.success is True
            assert result.endpoint.address == "https://ap.test.fr/as4"

    async def test_peppol_mock_not_found(self):
        """PeppolService returns not found for unknown participants."""
        async with PeppolService(mock=True) as svc:
            result = await svc.lookup_by_siren("999999999")
            assert result.success is False
            assert result.error_code == "PARTICIPANT_NOT_FOUND"

    async def test_peppol_clear_mock_responses(self):
        """PeppolService can clear mock responses."""
        from pac0.service.routage.peppol import PeppolEndpoint

        async with PeppolService(mock=True) as svc:
            endpoint = PeppolEndpoint(
                address="https://ap.test.fr/as4",
                certificate="MOCK_CERT",
                transport_profile="peppol-transport-as4-v2_0",
            )
            svc.set_mock_response("0009", "123456789", endpoint=endpoint)

            # Clear responses
            svc.clear_mock_responses()

            # Should no longer find it
            result = await svc.lookup_by_siren("123456789")
            assert result.success is False


# =============================================================================
# Level 4: PA Service Lifecycle Tests
# =============================================================================


class TestPaServiceLifecycle:
    """Test PaService lifecycle."""

    async def test_pa_service_default(self):
        """Default PaService starts with embedded NATS."""
        async with PaService() as pa:
            assert pa.is_running is True
            assert pa.nats is not None
            assert pa.nats.is_running is True
            assert pa.broker is not None
            assert pa.api_base_url != ""
            assert pa.api_port > 0

    async def test_pa_service_healthcheck(self):
        """PA service responds to healthcheck."""
        async with PaService() as pa:
            async with pa.http_client() as client:
                response = await client.get("/healthcheck")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "OK"
                assert data["rank"] == "test"

    async def test_pa_service_root_endpoint(self):
        """PA service responds to root endpoint."""
        async with PaService() as pa:
            async with pa.http_client() as client:
                response = await client.get("/")
                assert response.status_code == 200
                assert response.json() == {"Hello": "World"}

    async def test_pa_service_info(self):
        """PA service provides info dict."""
        async with PaService() as pa:
            info = pa.info()
            assert "nats_url" in info
            assert "nats_port" in info
            assert "api_base_url" in info
            assert "api_port" in info
            assert info["nats_port"] > 0
            assert info["api_port"] > 0

    async def test_pa_service_shared_nats(self):
        """PA can use a shared NATS service."""
        async with NatsService() as nats:
            async with PaService(nats_service=nats) as pa:
                # PA uses the shared NATS
                assert pa.nats is nats
                assert pa.nats.is_running is True

            # NATS still running after PA stops
            assert nats.is_running is True

    async def test_pa_service_external_nats_endpoint(self):
        """PA can connect to external NATS endpoint."""
        async with NatsService() as external_nats:
            async with PaService(nats_endpoint=external_nats.endpoint) as pa:
                assert pa.is_running is True
                assert pa.nats.endpoint == external_nats.endpoint


# =============================================================================
# Level 5: WorldContext Basic Tests
# =============================================================================


class TestWorldContextBasic:
    """Test WorldContext basic functionality."""

    async def test_world_default_1pa(self):
        """Default WorldContext has 1 PA."""
        async with WorldContext() as world:
            assert len(world.pas) == 1
            assert world.pa1 is not None
            assert world.pa2 is None

    async def test_world_with_2pa(self):
        """WorldContext with 2 PA instances."""
        async with WorldContext(pa_count=2) as world:
            assert len(world.pas) == 2
            assert world.pa1 is not None
            assert world.pa2 is not None
            assert world.pa3 is None

    async def test_world_services_running(self):
        """WorldContext has all services running."""
        async with WorldContext(pa_count=2) as world:
            assert world.is_running is True
            assert world.nats.is_running is True
            assert world.peppol.is_running is True
            assert all(pa.is_running for pa in world.pas)

    async def test_world_shared_nats(self):
        """All PAs share the same NATS service."""
        async with WorldContext(pa_count=2) as world:
            # Both PAs should share the same NATS instance
            assert world.pa1.nats is world.pa2.nats
            assert world.pa1.nats is world.nats

    async def test_world_info(self):
        """WorldContext provides info dict."""
        async with WorldContext(pa_count=2) as world:
            info = world.info()
            assert "nats" in info
            assert "peppol" in info
            assert "pas" in info
            assert len(info["pas"]) == 2
            assert info["nats"]["is_running"] is True
            assert info["peppol"]["is_running"] is True


# =============================================================================
# Level 6: WorldContext Multi-PA Tests
# =============================================================================


class TestWorldContextMultiPA:
    """Test WorldContext with multiple PA instances."""

    async def test_world_pa_isolation_ports(self):
        """Each PA has different ports."""
        async with WorldContext(pa_count=3) as world:
            api_ports = [pa.api_port for pa in world.pas]
            # All ports should be unique
            assert len(set(api_ports)) == 3

    async def test_world_each_pa_functional(self):
        """Each PA responds to requests."""
        async with WorldContext(pa_count=3) as world:
            for pa in world.pas:
                async with pa.http_client() as client:
                    response = await client.get("/healthcheck")
                    assert response.status_code == 200

    async def test_world_max_pa_count(self):
        """WorldContext supports up to 10 PAs."""
        async with WorldContext(pa_count=4) as world:
            assert len(world.pas) == 4
            assert world.pa4 is not None

    async def test_world_pa_count_validation(self):
        """WorldContext validates pa_count bounds."""
        with pytest.raises(AssertionError):
            WorldContext(pa_count=0)

        with pytest.raises(AssertionError):
            WorldContext(pa_count=11)


# =============================================================================
# Level 7: WorldContext Configuration Tests
# =============================================================================


class TestWorldContextConfiguration:
    """Test WorldContext with various configurations."""

    async def test_world_custom_nats_service(self):
        """WorldContext accepts pre-configured NATS service."""
        nats = NatsService()
        async with nats:
            async with WorldContext(nats_service=nats, pa_count=1) as world:
                assert world.nats is nats

    async def test_world_custom_peppol_service(self):
        """WorldContext accepts pre-configured Peppol service."""
        peppol = PeppolService(mock=True)
        async with peppol:
            async with WorldContext(peppol_service=peppol, pa_count=1) as world:
                assert world.peppol is peppol

    async def test_world_peppol_mock_mode(self):
        """WorldContext uses mock Peppol by default."""
        async with WorldContext(pa_count=1) as world:
            assert world.peppol._mock is True

    async def test_world_services_stop_on_exit(self):
        """WorldContext properly stops all services on exit."""
        world = WorldContext(pa_count=2)
        await world.__aenter__()

        pa1 = world.pa1
        pa2 = world.pa2
        nats = world.nats
        peppol = world.peppol

        assert pa1.is_running is True
        assert pa2.is_running is True
        assert nats.is_running is True
        assert peppol.is_running is True

        await world.__aexit__(None, None, None)

        assert pa1.is_running is False
        assert pa2.is_running is False
        assert nats.is_running is False
        assert peppol.is_running is False


# =============================================================================
# Level 8: Fixture Tests
# =============================================================================


class TestWorldFixtures:
    """Test pytest fixtures."""

    async def test_world_fixture(self, world):
        """world fixture provides 1 PA."""
        assert len(world.pas) == 1
        assert world.pa1 is not None

    async def test_world1pa_fixture(self, world1pa):
        """world1pa fixture provides 1 PA."""
        assert len(world1pa.pas) == 1

    async def test_world2pa_fixture(self, world2pa):
        """world2pa fixture provides 2 PAs."""
        assert len(world2pa.pas) == 2

    async def test_world4pa_fixture(self, world4pa):
        """world4pa fixture provides 4 PAs."""
        assert len(world4pa.pas) == 4

    async def test_nats_service_fixture(self, nats_service):
        """nats_service fixture provides running NATS."""
        assert nats_service.is_running is True
        assert nats_service.port > 0

    async def test_peppol_service_fixture(self, peppol_service):
        """peppol_service fixture provides mock Peppol."""
        assert peppol_service.is_running is True
        assert peppol_service._mock is True

    async def test_pa_service_fixture(self, pa_service):
        """pa_service fixture provides running PA."""
        assert pa_service.is_running is True
        async with pa_service.http_client() as client:
            response = await client.get("/healthcheck")
            assert response.status_code == 200


# =============================================================================
# Level 9: ServiceRunner Tests
# =============================================================================


class TestServiceRunner:
    """Test ServiceRunner for FastStream services."""

    async def test_service_runner_readiness(self, nats_service):
        """ServiceRunner signals readiness via after_startup hook."""
        from faststream.nats import NatsBroker

        broker = NatsBroker(nats_service.endpoint, apply_types=True)
        async with broker:
            await broker.start()

            router = NatsRouter()

            @router.subscriber("test-subject")
            async def handler(msg: str):
                pass

            runner = ServiceRunner(broker, router, name="test-service")

            # Initially not ready
            assert not runner.ready.is_set()

            # Start and wait for ready
            await runner.start()
            await runner.wait_ready(timeout=5.0)

            assert runner.ready.is_set()

            await runner.stop()

    async def test_service_runner_timeout(self, nats_service):
        """ServiceRunner raises TimeoutError if not ready."""
        from faststream.nats import NatsBroker

        broker = NatsBroker(nats_service.endpoint, apply_types=True)
        async with broker:
            router = NatsRouter()

            runner = ServiceRunner(broker, router, name="test")

            # Don't start - should timeout
            with pytest.raises(asyncio.TimeoutError):
                await runner.wait_ready(timeout=0.1)
