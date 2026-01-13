# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import FastAPI
from pac0.service.api_gateway.lib import router
from faststream.nats import NatsBroker
from faststream.nats.fastapi import NatsRouter

app = FastAPI()
app.state.rank = "dev"

# TODO: get url from env/settings
nats_router = NatsRouter("nats://localhost:4222")
app.include_router(nats_router)

app.state.broker = nats_router.broker

app.include_router(router)
