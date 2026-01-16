# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from dataclasses import dataclass
import functools
from typing import Any

import httpx
from pydantic import BaseModel
import pytest
from pac0.shared.test.world import WorldContext, world, world1
from pac0.shared.test.service.base import BaseServiceContext
from pac0.shared.test.service.fastapi import FastApiServiceContext
from pac0.shared.test.service.nats import NatsServiceContext
from pytest_bdd import given, parsers, scenario, then, when


# =====================================================================
# local BDD context class and fixtures

@dataclass
class LocalTestCtx:
    service: BaseServiceContext | None = None

    service_api_gateway: FastApiServiceContext | None = None
    service_esb_central: NatsServiceContext | None = None

    # TODO: make a typed result_request


# local BDD context fixture
@pytest.fixture
def ctx():
    """Contexte pour les tests BDD"""
    return LocalTestCtx()


@pytest.fixture
async def api_gateway_service(
    ctx: LocalTestCtx,
):
    if ctx.service_esb_central is None:
        raise Exception('esb service not instanciated')
    
    # TODO: move to BaseServiceContext
    nats_url = f"nats://{ctx.service_esb_central.config.host}:{ctx.service_esb_central.config.port}"
    async with FastApiServiceContext(nats_url=nats_url) as svc:
        yield svc


@pytest.fixture
async def esb_central_service():
    async with NatsServiceContext() as svc:
        yield svc

# =====================================================================
# BDD steps definition

# Quand je lance le service "01-api-gateway"
@when(
    parsers.parse('''je lance le service "01-api-gateway"'''),
)
def _(
    ctx: LocalTestCtx,
    api_gateway_service: FastApiServiceContext,
):
    ctx.service_api_gateway = api_gateway_service


# Quand je lance le service "02-esb-central"
@when(
    parsers.parse('''je lance le service "02-esb-central"'''),
)
def _(
    ctx: LocalTestCtx,
    esb_central_service: NatsServiceContext,
):
    ctx.service_esb_central = esb_central_service


# Alors le service "01-api-gateway" est prêt
@then("""le service "01-api-gateway" est prêt""")
def _(
    ctx: LocalTestCtx,
):
    assert ctx.service_api_gateway, "Le service n'est pas instancié"
    assert ctx.service_api_gateway.is_ready, "Le service n'est pas prêt"


# Alors le service "02-esb-central" est prêt
@then('''le service "02-esb-central" est prêt''')
def _(
    ctx: LocalTestCtx,
):
    assert ctx.service_esb_central, "Le service n'est pas instancié"
    assert ctx.service_esb_central.is_ready, "Le service n'est pas prêt"


# Alors le service "01-api-gateway" n'est pas prêt
@then('''le service "01-api-gateway" n'est pas prêt''')
def _(
    ctx: LocalTestCtx,
):
    if ctx.service_api_gateway:
        assert not ctx.service_api_gateway.is_ready, "Le service est prêt"


# Quand le service "02-esb-central" n'est pas prêt
# Alors le service "02-esb-central" n'est pas prêt
@when("""le service "02-esb-central" n'est pas prêt""")
@then("""le service "02-esb-central" n'est pas prêt""")
def _(
    ctx: LocalTestCtx,
):
    if ctx.service_esb_central:
        assert not ctx.service_esb_central.is_ready, "Le service est prêt"
