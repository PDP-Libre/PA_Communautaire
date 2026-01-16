# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import FastAPI
from pac0.service.api_gateway.lib.api import router as router_api
from pac0.service.api_gateway.lib.bus import router as router_bus

app = FastAPI()

app.include_router(router_bus)
app.include_router(router_api)

app.state.rank = "dev"
app.state.broker = router_bus.broker
