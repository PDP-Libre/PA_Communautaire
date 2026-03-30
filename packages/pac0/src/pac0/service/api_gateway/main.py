# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import FastAPI
from scalar_fastapi import OpenAPISource, get_scalar_api_reference

from pac0.service.api_gateway.lib.api import router as router_api
from pac0.service.api_gateway.lib.bus import router as router_bus

app = FastAPI()

app.include_router(router_bus)
app.include_router(router_api)

app.state.rank = "dev"
app.state.broker = router_bus.broker


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        # TODO: move this list to a config file
        sources=[
            OpenAPISource(title="pac0", url=app.openapi_url, default=True),
            OpenAPISource(
                title="superPDP directory",
                url="https://api.superpdp.tech/openapi/xp-z12-013-directory-1.2.0.json",
            ),
            OpenAPISource(
                title="superPDP flow",
                url="https://api.superpdp.tech/openapi/xp-z12-013-flow-1.2.0.json",
            ),
        ],
        title="pac0 PA/PDP openAPI",
    )
