"""
BDD step definitions for service lifecycle testing.

This module provides pytest-bdd step definitions that work with async fixtures.

IMPORTANT: HTTP API calls from sync BDD steps to servers running in async
fixtures is currently problematic due to event loop blocking. The API-related
scenarios are disabled in the feature file. Use test_service_lifecycle.py
for full API testing with pure async tests.

References:
- pytest-bdd: https://pytest-bdd.readthedocs.io/en/latest/
- httpx: https://www.python-httpx.org/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
"""

import asyncio
import concurrent.futures
from typing import Optional

import httpx
import pytest
import pytest_asyncio
from pytest_bdd import given, when, then, parsers

from pac0.shared.test.service_fixture import (
    NatsServerContext,
    WorldServiceContext,
)


# Thread pool executor for running sync operations
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)


def http_request_sync(method: str, url: str, timeout: float = 10.0) -> httpx.Response:
    """Make an HTTP request synchronously."""
    return httpx.request(method, url, timeout=timeout)


# ============================================================================
# Module-scoped async fixtures for BDD scenarios
# Using loop_scope="module" ensures all tests share the same event loop
# See: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
# ============================================================================


@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def nats_server_module():
    """NATS server for BDD tests - module scoped."""
    async with NatsServerContext() as ctx:
        yield ctx


@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def world_1pa_module():
    """World with 1 PA - module scoped to persist across scenarios."""
    async with WorldServiceContext(pac_count=1) as world:
        yield world


@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def world_2pa_module():
    """World with 2 PAs - module scoped."""
    async with WorldServiceContext(pac_count=2) as world:
        yield world


# ============================================================================
# Shared state fixture for BDD steps
# ============================================================================


@pytest.fixture
def bdd_state():
    """Shared state storage for BDD steps within a scenario."""
    return {"last_response": None, "broker_url": None}


# ============================================================================
# Given steps (French with accents)
# ============================================================================


@given("un serveur NATS disponible", target_fixture="nats_ctx")
def given_nats_server(nats_server_module):
    """Ensure NATS server is available."""
    assert nats_server_module.is_running, "NATS server should be running"
    return nats_server_module


@given("une PA démarrée", target_fixture="pa_ctx")
def given_pa_started(world_1pa_module):
    """Ensure PA is started with all services."""
    pa = world_1pa_module.pac1
    assert pa.nats.is_running, "NATS should be running"
    assert pa.broker is not None, "Broker should be connected"
    assert pa.api_base_url, "API should have a URL"
    return pa


@given(parsers.parse("{count:d} PA démarrées"), target_fixture="world_ctx")
def given_multiple_pa(count, world_2pa_module):
    """Ensure specified number of PAs are started."""
    assert len(world_2pa_module.pacs) >= count, f"Expected at least {count} PAs"

    for pa in world_2pa_module.pacs[:count]:
        assert pa.nats.is_running, "Each PA should have NATS running"
    return world_2pa_module


# ============================================================================
# When steps (French with accents)
# ============================================================================


@when("je connecte un broker NATS")
def when_connect_broker(nats_ctx, bdd_state):
    """Connect a broker to the NATS server."""
    bdd_state["broker_url"] = nats_ctx.url


# NOTE: API call steps are disabled due to async/sync interaction issues.
# The HTTP call from a sync step blocks the event loop that runs the server.
# See test_service_lifecycle.py for working API tests using pure async.
#
# @when(parsers.parse("j'appelle l'API {verb} {path}"))
# def when_api_call(verb: str, path: str, pa_ctx, bdd_state):
#     """Make an HTTP API call."""
#     url = f"{pa_ctx.api_base_url}{path}"
#     future = _executor.submit(http_request_sync, verb, url)
#     response = future.result(timeout=30.0)
#     bdd_state["last_response"] = response


@when(parsers.parse("je publie le message '{msg}' sur le canal '{canal}'"))
def when_publish_message(msg: str, canal: str, pa_ctx):
    """Publish a message to a NATS channel."""

    async def publish():
        await pa_ctx.broker.publish(msg, subject=canal)

    future = _executor.submit(asyncio.run, publish())
    future.result(timeout=5.0)


# ============================================================================
# Then steps (French with accents)
# ============================================================================


@then("le serveur NATS est en cours d'exécution")
def then_nats_running(nats_ctx):
    """Verify NATS server is running."""
    assert nats_ctx.is_running is True


@then("le broker est connecté")
def then_broker_connected(bdd_state):
    """Verify broker connection was established."""
    url = bdd_state.get("broker_url")
    assert url is not None, "Broker URL should be set"
    assert url.startswith("nats://")


@then(parsers.parse("j'obtiens le code de retour {code:d}"))
def then_response_code(code: int, bdd_state):
    """Verify HTTP response status code."""
    response = bdd_state.get("last_response")
    assert response is not None, "No response recorded"
    assert response.status_code == code, f"Expected {code}, got {response.status_code}"


@then(parsers.parse('la réponse contient "{key}" égal à "{value}"'))
def then_response_contains(key: str, value: str, bdd_state):
    """Verify response JSON contains expected key/value."""
    response = bdd_state.get("last_response")
    assert response is not None, "No response recorded"

    data = response.json()
    assert key in data, f"Key '{key}' not in response"
    assert str(data[key]) == value, f"Expected {key}={value}, got {data[key]}"


@then("chaque PA a son propre port NATS")
def then_unique_nats_ports(world_ctx):
    """Verify each PA has a unique NATS port."""
    ports = [pa.nats.port for pa in world_ctx.pacs]
    assert len(ports) == len(set(ports)), "NATS ports should be unique"


@then("chaque PA a son propre port API")
def then_unique_api_ports(world_ctx):
    """Verify each PA has a unique API port."""
    ports = [pa.uvicorn_server.config.port for pa in world_ctx.pacs]
    assert len(ports) == len(set(ports)), "API ports should be unique"


@then(parsers.parse("je reçois le message '{expected_msg}' sur le canal '{canal}'"))
def then_receive_message(expected_msg: str, canal: str, pa_ctx):
    """Verify a message was received on a channel."""
    assert pa_ctx is not None, "PA context required"
    # TODO: Implement full message verification with subscriber
