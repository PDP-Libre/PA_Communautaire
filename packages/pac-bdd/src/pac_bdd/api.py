# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import functools
from typing import Any

import httpx
from pydantic import BaseModel
import pytest
from pac0.shared.test.world import WorldContext, world, world1
from pytest_bdd import given, parsers, scenario, then, when


# local BDD context class
class LocalTestCtx(BaseModel):
    result: Any | None = None
    result_status_code: int | None = None
    # TODO: make a typed result_request


# local BDD context fixture
@pytest.fixture
def ctx():
    """Contexte pour les tests BDD"""
    return LocalTestCtx()


# Soit une pa communautaire
@given("""une pa communautaire""")
def _(
    world1: WorldContext,
):
    pass


# Quand j'appele l'API GET /healthcheck
@when(
    parsers.parse("j'appele l'API {verb} {path}"),
)
def _(
    ctx: LocalTestCtx,
    world1: WorldContext,
    verb: str,
    path: str,
):
    with world1.pa1.api_gateway.get_client() as client:
        response = client.request(verb, path)
        ctx.result_status_code = response.status_code
        ctx.result_json = response.json()
        # TODO: not a good idea to store a context manager outside its scope
        ctx.result = response


# Alors j'obtiens le code de retour 200
@then(parsers.parse("""j'obtiens le code de retour {code}"""))
def _(
    ctx: LocalTestCtx,
    code: str,
):
    # assert response.status_code == 200
    assert ctx.result_status_code == int(code)


# Et la réponse a une clé "healthcheck_resp" avec 2 éléments
@then(parsers.parse("""la réponse a une clé "{key}" avec {nb} éléments"""))
def _(
    ctx: LocalTestCtx,
    key: str,
    nb: str,
):
    assert len(ctx.result_json.get(key)) == int(nb)
