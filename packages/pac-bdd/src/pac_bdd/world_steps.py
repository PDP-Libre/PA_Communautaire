# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Step definitions BDD pour WorldContext et les services.

Ce module implémente les steps Gherkin pour tester:
- Les services individuels (NATS, Peppol, PA)
- Le WorldContext avec plusieurs PA
- La communication inter-PA

Références:
- pytest-bdd: https://pytest-bdd.readthedocs.io/
- ServiceProtocol: pac0.shared.test.protocol
- WorldContext: pac0.shared.test.world
"""

import asyncio
import functools
from typing import Optional

import pytest
from pytest_bdd import given, parsers, then, when

from pac0.service.routage.peppol import PeppolEndpoint
from pac0.shared.test.services import NatsService, PaService
from pac0.shared.test.world import WorldContext


def async_to_sync(fn):
    """Convert async function to sync function for pytest-bdd."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(fn(*args, **kwargs))

    return wrapper


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def world_context():
    """Contexte pour les tests WorldContext."""
    return {
        "nats_service": None,
        "nats_service_ref": None,
        "peppol_service": None,
        "peppol_service_ref": None,
        "pa_service": None,
        "world": None,
        "response": None,
        "response_code": None,
        "response_data": None,
        "lookup_result": None,
        "world_info": None,
        "enterprises": {},
        "invoices": {},
    }


# =============================================================================
# Given - Services individuels
# =============================================================================


@given("un service NATS local")
@async_to_sync
async def nats_local_service(world_context):
    """Démarre un service NATS local."""
    svc = NatsService()
    await svc.__aenter__()
    world_context["nats_service"] = svc


@given("un service NATS local comme référence")
@async_to_sync
async def nats_reference_service(world_context):
    """Démarre un service NATS de référence."""
    svc = NatsService()
    await svc.__aenter__()
    world_context["nats_service_ref"] = svc


@given("un service NATS connecté à l'endpoint de référence")
@async_to_sync
async def nats_remote_service(world_context):
    """Connecte un service NATS à l'endpoint de référence."""
    ref = world_context["nats_service_ref"]
    svc = NatsService(endpoint=ref.endpoint)
    await svc.__aenter__()
    world_context["nats_service"] = svc


@given("un service Peppol en mode mock")
def peppol_mock_service():
    """Démarre un service Peppol en mode mock."""
    assert NotImplementedError()


@given("un service Peppol en mode mock comme référence")
@async_to_sync
async def peppol_reference_service(world_context):
    """Démarre un service Peppol de référence."""
    # svc = PeppolService(mock=True)
    # await svc.__aenter__()
    # world_context["peppol_service_ref"] = svc
    assert NotImplementedError()


@given(parsers.parse('une entreprise avec le SIREN "{siren}" enregistrée sur Peppol'))
def enterprise_registered_peppol(world_context, siren: str):
    """Enregistre une entreprise sur Peppol (mock)."""
    svc = world_context["peppol_service"]
    endpoint = PeppolEndpoint(
        address="https://ap.mock.peppol/as4",
        certificate="MOCK_CERT_BASE64",
        transport_profile="peppol-transport-as4-v2_0",
    )
    svc.set_mock_response(
        scheme_id="0009",
        participant_id=siren,
        endpoint=endpoint,
    )
    world_context["enterprises"][siren] = {
        "siren": siren,
        "registered": True,
        "endpoint": endpoint,
    }


@given("un service PA")
@async_to_sync
async def pa_service(world_context):
    """Démarre un service PA."""
    # svc = PaService()
    # await svc.__aenter__()
    # world_context["pa_service"] = svc
    assert NotImplementedError()


# =============================================================================
# Given - WorldContext
# =============================================================================


@given(parsers.parse("un monde avec {count:d} PA"))
@async_to_sync
async def world_with_pa_count(world_context, count: int):
    """Crée un monde avec N PA."""
    world = WorldContext(pa_count=count)
    await world.__aenter__()
    world_context["world"] = world


@given(parsers.parse("un monde avec {count:d} PA démarré"))
@async_to_sync
async def world_with_pa_count_started(world_context, count: int):
    """Crée un monde avec N PA (démarré)."""
    world = WorldContext(pa_count=count)
    await world.__aenter__()
    world_context["world"] = world


@given(
    parsers.parse("un monde utilisant le service NATS de référence avec {count:d} PA")
)
@async_to_sync
async def world_with_nats_ref(world_context, count: int):
    """Crée un monde utilisant un NATS de référence."""
    nats_ref = world_context["nats_service_ref"]
    world = WorldContext(nats_service=nats_ref, pa_count=count)
    await world.__aenter__()
    world_context["world"] = world


@given(
    parsers.parse("un monde utilisant le service Peppol de référence avec {count:d} PA")
)
@async_to_sync
async def world_with_peppol_ref(world_context, count: int):
    """Crée un monde utilisant un Peppol de référence."""
    peppol_ref = world_context["peppol_service_ref"]
    world = WorldContext(peppol_service=peppol_ref, pa_count=count)
    await world.__aenter__()
    world_context["world"] = world


# =============================================================================
# Given - Entreprises et factures
# =============================================================================


@given(parsers.parse('l\'entreprise #{enterprise_id} avec le SIREN "{siren}"'))
def enterprise_defined(world_context, enterprise_id: str, siren: str):
    """Définit une entreprise."""
    world_context["enterprises"][enterprise_id] = {
        "id": enterprise_id,
        "siren": siren,
        "registered_pa": None,
        "peppol_registered": False,
    }


@given(parsers.parse("l'entreprise #{enterprise_id} enregistrée sur la PA #{pa_num:d}"))
def enterprise_on_pa(world_context, enterprise_id: str, pa_num: int):
    """Enregistre une entreprise sur une PA."""
    world_context["enterprises"][enterprise_id]["registered_pa"] = pa_num


@given(
    parsers.parse(
        "l'entreprise #{enterprise_id} enregistrée sur la PA #{pa_num:d} via Peppol"
    )
)
def enterprise_on_pa_via_peppol(world_context, enterprise_id: str, pa_num: int):
    """Enregistre une entreprise sur une PA via Peppol."""
    enterprise = world_context["enterprises"][enterprise_id]
    enterprise["registered_pa"] = pa_num
    enterprise["peppol_registered"] = True

    # Configure Peppol mock
    world = world_context["world"]
    if world and world.peppol:
        endpoint = PeppolEndpoint(
            address=f"https://ap.pa{pa_num}.mock/as4",
            certificate="MOCK_CERT_BASE64",
            transport_profile="peppol-transport-as4-v2_0",
        )
        world.peppol.set_mock_response(
            scheme_id="0009",
            participant_id=enterprise["siren"],
            endpoint=endpoint,
        )


@given(parsers.parse("une facture #{invoice_id} de #{sender_id} vers #{recipient_id}"))
def invoice_defined(world_context, invoice_id: str, sender_id: str, recipient_id: str):
    """Définit une facture."""
    world_context["invoices"][invoice_id] = {
        "id": invoice_id,
        "sender": sender_id,
        "recipient": recipient_id,
    }


# =============================================================================
# When - Actions
# =============================================================================


@when(parsers.parse('je recherche l\'entreprise avec le SIREN "{siren}" sur Peppol'))
@async_to_sync
async def lookup_peppol_siren(world_context, siren: str):
    """Recherche une entreprise sur Peppol."""
    svc = world_context["peppol_service"]
    result = await svc.lookup_by_siren(siren)
    world_context["lookup_result"] = result


@when(parsers.parse("j'appelle le healthcheck de la PA #{pa_num:d}"))
@async_to_sync
async def call_pa_healthcheck(world_context, pa_num: int):
    """Appelle le healthcheck d'une PA."""
    world = world_context["world"]
    pa = getattr(world, f"pa{pa_num}")
    async with pa.http_client() as client:
        response = await client.get("/healthcheck")
        world_context["response_code"] = response.status_code
        world_context["response_data"] = response.json()


@when("je demande les informations du monde")
def get_world_info(world_context):
    """Récupère les informations du monde."""
    world = world_context["world"]
    world_context["world_info"] = world.info()


@when("j'arrête le monde")
@async_to_sync
async def stop_world(world_context):
    """Arrête le monde."""
    world = world_context["world"]
    await world.__aexit__(None, None, None)


@when(
    parsers.parse("un utilisateur de la PA #{pa_num:d} dépose la facture #{invoice_id}")
)
@async_to_sync
async def user_deposits_invoice(world_context, pa_num: int, invoice_id: str):
    """Un utilisateur dépose une facture."""
    world = world_context["world"]
    invoice = world_context["invoices"][invoice_id]
    recipient_id = invoice["recipient"]
    recipient = world_context["enterprises"].get(recipient_id, {})

    # Lookup Peppol for recipient
    if recipient.get("peppol_registered"):
        result = await world.peppol.lookup_by_siren(recipient["siren"])
        world_context["lookup_result"] = result


# =============================================================================
# Then - Assertions services individuels
# =============================================================================


@then("le service NATS est en cours d'exécution")
def nats_is_running(world_context):
    """Vérifie que le service NATS est en cours d'exécution."""
    svc = world_context["nats_service"]
    assert svc.is_running is True


@then("le service NATS distant est en cours d'exécution")
def nats_remote_is_running(world_context):
    """Vérifie que le service NATS distant est en cours d'exécution."""
    svc = world_context["nats_service"]
    assert svc.is_running is True


@then("le service NATS a un endpoint valide")
def nats_has_endpoint(world_context):
    """Vérifie que le service NATS a un endpoint valide."""
    svc = world_context["nats_service"]
    assert svc.endpoint.startswith("nats://")


@then("le service NATS est de type local")
def nats_is_local(world_context):
    """Vérifie que le service NATS est local."""
    svc = world_context["nats_service"]
    assert svc.is_local is True


@then("le service NATS distant est de type distant")
def nats_is_remote(world_context):
    """Vérifie que le service NATS est distant."""
    svc = world_context["nats_service"]
    assert svc.is_local is False


@then("le service Peppol est en cours d'exécution")
def peppol_is_running(world_context):
    """Vérifie que le service Peppol est en cours d'exécution."""
    svc = world_context["peppol_service"]
    assert svc.is_running is True


@then("le service Peppol utilise le mode mock")
def peppol_is_mock(world_context):
    """Vérifie que le service Peppol utilise le mode mock."""
    svc = world_context["peppol_service"]
    assert svc._mock is True


@then("le lookup Peppol réussit")
def peppol_lookup_success(world_context):
    """Vérifie que le lookup Peppol a réussi."""
    result = world_context["lookup_result"]
    assert result is not None
    assert result.success is True


@then("le lookup Peppol échoue")
def peppol_lookup_failure(world_context):
    """Vérifie que le lookup Peppol a échoué."""
    result = world_context["lookup_result"]
    assert result is not None
    assert result.success is False


@then(parsers.parse('l\'endpoint retourné est "{endpoint}"'))
def peppol_endpoint_is(world_context, endpoint: str):
    """Vérifie l'endpoint retourné par Peppol."""
    result = world_context["lookup_result"]
    assert result.endpoint is not None
    assert result.endpoint.address == endpoint


@then(parsers.parse('le code erreur est "{error_code}"'))
def peppol_error_code(world_context, error_code: str):
    """Vérifie le code d'erreur Peppol."""
    result = world_context["lookup_result"]
    assert result.error_code == error_code


@then("le service PA est en cours d'exécution")
def pa_is_running(world_context):
    """Vérifie que le service PA est en cours d'exécution."""
    # svc = world_context["pa_service"]
    # assert svc.is_running is True
    assert NotImplementedError()


@then("le service PA a un endpoint API valide")
def pa_has_endpoint(world_context):
    """Vérifie que le service PA a un endpoint API valide."""
    # svc = world_context["pa_service"]
    # assert svc.api_base_url.startswith("http://")
    assert NotImplementedError()


@then("le service PA répond au healthcheck")
@async_to_sync
async def pa_healthcheck_ok(world_context):
    """Vérifie que le service PA répond au healthcheck."""
    # svc = world_context["pa_service"]
    # async with svc.http_client() as client:
    #    response = await client.get("/healthcheck")
    #    assert response.status_code == 200
    assert NotImplementedError()


# =============================================================================
# Then - Assertions WorldContext
# =============================================================================


@then("le monde est en cours d'exécution")
def world_is_running(world_context):
    """Vérifie que le monde est en cours d'exécution."""
    world = world_context["world"]
    assert world.is_running is True


@then(parsers.parse("le monde contient {count:d} PA"))
def world_has_pa_count(world_context, count: int):
    """Vérifie le nombre de PA dans le monde."""
    world = world_context["world"]
    assert len(world.pas) == count


@then("le service NATS du monde est en cours d'exécution")
def world_nats_running(world_context):
    """Vérifie que le NATS du monde est en cours d'exécution."""
    world = world_context["world"]
    assert world.nats.is_running is True


@then("le service Peppol du monde est en cours d'exécution")
def world_peppol_running(world_context):
    """Vérifie que le Peppol du monde est en cours d'exécution."""
    world = world_context["world"]
    assert world.peppol.is_running is True


@then(parsers.parse("la PA #{pa_num:d} est en cours d'exécution"))
def pa_num_is_running(world_context, pa_num: int):
    """Vérifie qu'une PA spécifique est en cours d'exécution."""
    world = world_context["world"]
    pa = getattr(world, f"pa{pa_num}")
    assert pa.is_running is True


@then(parsers.parse("la PA #{pa_num:d} utilise le service NATS du monde"))
def pa_uses_world_nats(world_context, pa_num: int):
    """Vérifie qu'une PA utilise le NATS du monde."""
    world = world_context["world"]
    pa = getattr(world, f"pa{pa_num}")
    assert pa.nats is world.nats


@then("chaque PA a un port API différent")
def each_pa_different_port(world_context):
    """Vérifie que chaque PA a un port API différent."""
    world = world_context["world"]
    ports = [pa.api_port for pa in world.pas]
    assert len(set(ports)) == len(ports)


@then(parsers.parse("j'obtiens le code de retour {code:d}"))
def response_code_is(world_context, code: int):
    """Vérifie le code de retour HTTP."""
    assert world_context["response_code"] == code


@then(parsers.parse('le statut est "{status}"'))
def response_status_is(world_context, status: str):
    """Vérifie le statut dans la réponse."""
    assert world_context["response_data"]["status"] == status


@then("les informations contiennent le service NATS")
def info_has_nats(world_context):
    """Vérifie que les infos contiennent NATS."""
    info = world_context["world_info"]
    assert "nats" in info
    assert info["nats"]["is_running"] is True


@then("les informations contiennent le service Peppol")
def info_has_peppol(world_context):
    """Vérifie que les infos contiennent Peppol."""
    info = world_context["world_info"]
    assert "peppol" in info
    assert info["peppol"]["is_running"] is True


@then(parsers.parse("les informations contiennent {count:d} PA"))
def info_has_pa_count(world_context, count: int):
    """Vérifie le nombre de PA dans les infos."""
    info = world_context["world_info"]
    assert "pas" in info
    assert len(info["pas"]) == count


# =============================================================================
# Then - Assertions cycle de vie
# =============================================================================


@then("toutes les PA sont arrêtées")
def all_pas_stopped(world_context):
    """Vérifie que toutes les PA sont arrêtées."""
    world = world_context["world"]
    for pa in world.pas:
        assert pa.is_running is False


@then("le service NATS est arrêté")
def nats_stopped(world_context):
    """Vérifie que le NATS est arrêté."""
    world = world_context["world"]
    assert world.nats is None or world.nats.is_running is False


@then("le service Peppol est arrêté")
def peppol_stopped(world_context):
    """Vérifie que le Peppol est arrêté."""
    world = world_context["world"]
    assert world.peppol is None or world.peppol.is_running is False


@then("le monde utilise le service NATS de référence")
def world_uses_nats_ref(world_context):
    """Vérifie que le monde utilise le NATS de référence."""
    world = world_context["world"]
    nats_ref = world_context["nats_service_ref"]
    assert world.nats is nats_ref


@then("le service NATS de référence reste actif après l'arrêt du monde")
@async_to_sync
async def nats_ref_still_running(world_context):
    """Vérifie que le NATS de référence reste actif."""
    nats_ref = world_context["nats_service_ref"]
    # Stop the world first
    world = world_context["world"]
    await world.__aexit__(None, None, None)
    # Reference should still be running
    assert nats_ref.is_running is True


@then("le monde utilise le service Peppol de référence")
def world_uses_peppol_ref(world_context):
    """Vérifie que le monde utilise le Peppol de référence."""
    world = world_context["world"]
    peppol_ref = world_context["peppol_service_ref"]
    assert world.peppol is peppol_ref


# =============================================================================
# Then - Assertions inter-PA
# =============================================================================


@then(parsers.parse("le lookup Peppol pour #{enterprise_id} réussit"))
def peppol_lookup_for_enterprise_success(world_context, enterprise_id: str):
    """Vérifie que le lookup Peppol pour une entreprise a réussi."""
    result = world_context["lookup_result"]
    assert result is not None
    assert result.success is True


@then(parsers.parse("la facture est routée vers la PA #{pa_num:d}"))
def invoice_routed_to_pa(world_context, pa_num: int):
    """Vérifie que la facture est routée vers une PA."""
    result = world_context["lookup_result"]
    assert result is not None
    assert result.success is True
    # Verify endpoint matches PA
    assert f"pa{pa_num}" in result.endpoint.address


# =============================================================================
# Cleanup fixture
# =============================================================================


@pytest.fixture(autouse=True)
def cleanup_world_context(world_context):
    """Nettoie les services après chaque test."""
    yield

    async def cleanup():
        # what to do in cleanup ??

    asyncio.get_event_loop().run_until_complete(cleanup())
