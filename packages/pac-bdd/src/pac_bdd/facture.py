# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import logging

import pytest
from pac0.shared.test.world import WorldContext, world, world1
from pytest_bdd import given, parsers, scenario, then, when

from pac_bdd.lib import reffile

logger = logging.getLogger(__name__)


## local BDD context class
# class LocalTestCtx(BaseModel):
#    result: Any | None = None
#    result_status_code: int | None = None
#    # TODO: make a typed result_request
#
#
## local BDD context fixture
# @pytest.fixture
# def ctx():
#    """Contexte pour les tests BDD"""
#    return LocalTestCtx()


# Note: "l'entreprise #{enterprise_id} enregistrée sur la PA #{pa_id}" is now defined in peppol.py
# Note: "la facture #{invoice_id} de #{sender_id} à #{recipient_id}" is now defined in peppol.py
# Note: "je dépose la facture #{invoice_id}" is now defined in peppol.py


# @when(parsers.parse("je dépose la facture #{invoice} sur #{pa}"))
# def submit_invoice_on_pa(invoice, pa):
#    # POST /
#    raise NotImplementedError()


@when(parsers.parse("je dépose la facture {invoice}"))
def _(
    world1: WorldContext,
    invoice: str,
):
    logger.debug(f"{invoice=}")

    invoice = reffile.resolve(invoice)
    with world1.pa1.api_gateway.get_client() as client:
        # TODO: attacher le fichier
        files = {"upload_file": invoice}
        # response = client.post("/flows")
        response = client.post("/flows", files=files)

        # TODO: recuperer le numero de job
        print(response.status_code)
        assert response.status_code == 200
    # TODO: attendre la fin du job via des appels reguliers api
    # raise NotImplementedError()


@when("je dépose une facture")
def _():
    # POST /
    raise NotImplementedError()


@when(
    parsers.parse("je dépose pour contrôle la facture @{invoice}"),
)
def control_invoice():
    raise NotImplementedError()


@then(parsers.parse("""un message arrive sur le {canal}"""))
def _(
    world1: WorldContext,
    canal: str,
):
    logger.debug(f"xxxx {canal=}")
    # print(f"xxxxxxxxxxxxxxxxxxxxxxx3 {len(world1.pa.esb_central.spy_log)=}")
    raise NotImplementedError()
