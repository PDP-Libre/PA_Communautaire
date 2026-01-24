# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from pac0.shared.test.world import WorldContext, world, world1


# Note: "l'entreprise #{enterprise_id} enregistrée sur la PA #{pa_id}" is now defined in peppol.py
# Note: "la facture #{invoice_id} de #{sender_id} à #{recipient_id}" is now defined in peppol.py
# Note: "je dépose la facture #{invoice_id}" is now defined in peppol.py


@when(parsers.parse("je dépose la facture #{invoice}"))
def submit_invoice(
    world1: WorldContext,
    invoice: str,
):
    with world1.pa1.api_gateway.get_client() as client:
        response = client.post("/flows")
        ctx.result_status_code = response.status_code
        ctx.result_json = response.json()
        # TODO: not a good idea to store a context manager outside its scope
        ctx.result = response
    raise NotImplementedError()


@when("je dépose une facture")
def submit_invoice_simple():
    # POST /
    raise NotImplementedError()


@when(parsers.parse("je dépose la facture #{invoice} sur #{pa}"))
def submit_invoice_on_pa(invoice, pa):
    # POST /
    raise NotImplementedError()


@when(
    parsers.parse("je dépose pour contrôle la facture @{invoice}"),
)
def control_invoice():
    raise NotImplementedError()
