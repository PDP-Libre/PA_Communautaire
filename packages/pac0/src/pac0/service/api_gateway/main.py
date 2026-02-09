# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
import yaml
from pac0.service.api_gateway.lib.api import router as router_api
from pac0.service.api_gateway.lib.bus import router as router_bus
import logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    # see https://fastapi.tiangolo.com/advanced/events/?h=#lifespan
    # we use lifespan to differ broker connexion
    # the API must start even if the broker is not available
    app.include_router(router_bus)
    app.state.broker = router_bus.broker
    yield
    # nothing to do at shutdown


# app = FastAPI(lifespan=lifespan)
app = FastAPI()
app.include_router(router_api)
app.include_router(router_bus)
app.state.broker = router_bus.broker
app.state.rank = "dev"

