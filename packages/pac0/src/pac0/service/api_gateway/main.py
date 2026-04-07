# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import FastAPI

from pac0.service.api_gateway.config import Settings
from pac0.service.api_gateway.lib import api, proxy
from pac0.service.api_gateway.lib.api import router as router_api
from pac0.service.api_gateway.lib.bus import router as router_bus
from pac0.service.api_gateway.lib.proxy import init_config
from pac0.service.api_gateway.lib.proxy import router as router_proxy

# Load configuration from YAML file
config = Settings.load_from_yaml("pac0_proxy.conf.yaml")

# Initialize proxy router with configuration
init_config(config)

app = FastAPI()

# proxy mode or handle PA API calls
if config.proxy.enabled:
    app.include_router(router_proxy)
    proxy.print_banner()
else:
    app.include_router(router_api)
    # In proxy v0 we don't want the 02-ESB connection
    app.include_router(router_bus)
    app.state.broker = router_bus.broker
    api.print_banner()

# In proxy v2+ we probably need a report router
# app.include_router(router_report)

app.state.rank = "dev"
