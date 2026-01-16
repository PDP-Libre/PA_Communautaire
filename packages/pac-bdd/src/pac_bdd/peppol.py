# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Step definitions BDD pour les tests PEPPOL.

Ce module implémente les steps Gherkin pour tester le service
de découverte PEPPOL et le routage inter-PA.
"""

import asyncio
import functools
import hashlib
from typing import Any, Optional

from pydantic import BaseModel
import pytest
import yaml
from pac0.shared.peppol import (
    compute_participant_hash,
    compute_sml_hostname,
    PeppolScheme,
)
from pytest_bdd import given, parsers, then, when

"""
from pac0.service.routage import (
    InvoiceMessage,
    PeppolEndpoint,
    PeppolEnvironment,
    PeppolLookupResult,
    PeppolLookupService,
    RoutingResult,
    RoutingStatus,
    route_invoice,
    set_peppol_service,
)
"""

def async_to_sync(fn):
    """Convert async function to sync function."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return asyncio.run(fn(*args, **kwargs))

    return wrapper


# =============================================================================
# Fixtures
# =============================================================================


class PeppolContext(BaseModel):
    sml_zone: str = "acc.edelivery.tech.ec.europa.eu"
    enterprise_id: str | None = None
    siren: str | None = None
    siret: str | None = None
    result: Any | None = None  # PeppolLookupResult


#    peppol_context["enterprises"][enterprise_id] = {
#        "siren": siren,
#        "siret": None,
#        "registered": False,
#        "scheme": "0009",
#        "smp_url": None,
#        "endpoint": None,
#    }


@pytest.fixture
def peppol_context():
    """Contexte pour les tests PEPPOL."""
    """
    return {
        "environment": PeppolEnvironment.TEST,
        "sml_zone": "acc.edelivery.tech.ec.europa.eu",
        "enterprises": {},  # {id: {siren, siret, registered, scheme, smp_url, endpoint}}
        "invoices": {},  # {id: InvoiceMessage}
        "pas": {},  # {id: {enterprises: []}}
        "lookup_result": None,  # PeppolLookupResult
        "routing_result": None,  # RoutingResult
        "peppol_service": None,  # PeppolLookupService
        "dns_responses": {},  # {hostname: smp_url}
        "smp_hostname": None,
        "dns_error": None,
    }
    """
    return PeppolContext()

'''
@pytest.fixture
def peppol_service(peppol_context) -> PeppolLookupService:
    """Service PEPPOL configuré pour les tests."""

    def mock_dns_resolver(hostname: str) -> Optional[str]:
        """Résolveur DNS mock pour les tests."""
        return peppol_context["dns_responses"].get(hostname)

    service = PeppolLookupService(
        environment=peppol_context["environment"],
        dns_resolver=mock_dns_resolver,
    )
    peppol_context["peppol_service"] = service
    set_peppol_service(service)
    return service
'''

# =============================================================================


@when(parsers.parse('''je calcule l'empreinte md5 de "{msg}"'''))
def _(peppol_context: PeppolContext, msg: str):
    peppol_context.result = hashlib.md5(msg.encode("utf-8")).hexdigest()


@then(parsers.parse('''j'obtiens "{result}"'''))
def _(
    peppol_context: PeppolContext,
    result: str,
):
    """étape générique pour tester tout résultat"""
    if peppol_context.result != result:
        print(f"result: {peppol_context.result}")
        print(f"expecting: {result}")
    assert peppol_context.result == result


@then(parsers.parse('''l'identification par {facon} porte le code "{code}"'''))
def _(
    facon: str,
    code: str,
):
    print("xxxx", getattr(PeppolScheme, facon).value, code)
    assert getattr(PeppolScheme, facon).value == code


@when(parsers.parse('''je calcule l'empreinte {facon} "{id}"'''))
def _(
    peppol_context: PeppolContext,
    facon: str,
    id: str,
):
    peppol_context.result = compute_participant_hash(facon, id)


@given(parsers.parse('''la racine SML "{zone}"'''))
def _(
    peppol_context: PeppolContext,
    zone: str,
):
    peppol_context.sml_zone = zone


@when(parsers.parse('''je calcule l'hôte SML pour {facon} "{id}"'''))
def _(
    peppol_context: PeppolContext,
    facon: str,
    id: str,
):
    peppol_context.result = compute_sml_hostname(
        sml_zone=peppol_context.sml_zone,
        scheme_id=facon,
        participant_id=id,
    )


# compute_sml_hostname
# =============================================================================


@given(parsers.parse("le service PEPPOL simulé avec:"))
def _(
    world,
    datatable,
):
    """Configure le service PEPPOL simulé."""
    # peppol_data = yaml.safe_load(docstring)

    # ou

    """
    sml: acc.edelivery.tech.ec.europa.eu
    entreprises:
    - id: e1
        smp: https://smp.pa-distante.fr
    - id: e2
        smp: https://smp.autre-pa.fr
    """

    print(datatable)
