# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from typing import Any
from pydantic_settings import BaseSettings
from faststream import FastStream, ContextRepo
import os
from faststream.nats import NatsBroker, NatsRouter

QUEUE = "q"


class SettingsService(BaseSettings):
    # any_flag: bool
    ...


@dataclass
class CtxService:
    prefix: str
    queue: str
    broker: Any
    subject_in: str
    subject_out: str
    subject_err: str
    publisher_out: Any
    publisher_err: Any


def init_esb_app(prefix):
    global broker

    _broker = NatsBroker(get_nats_url())

    app = FastStream(_broker)
    _broker.include_router(router)

    broker = _broker

    subject_in = f"{prefix}-IN"
    subject_out = f"{prefix}-OUT"
    subject_err = f"{prefix}-ERR"

    ctx = CtxService(
        prefix=prefix,
        queue=QUEUE,
        broker=_broker,
        subject_in=subject_in,
        subject_out=subject_out,
        subject_err=subject_err,
        publisher_out=_broker.publisher(subject_out),
        publisher_err=_broker.publisher(subject_err),
    )

    # You MUST return broker and app separatly
    return ctx, _broker, app


# TODO: deprecate
def init_esb_app_old():
    # TODO: use router to allow dynamic router setup
    # broker.include_router(router)
    # broker = NatsBroker("nats://demo.nats.io:4222")
    broker = NatsBroker("nats://localhost:4222")
    app = FastStream(broker)
    publisher_ping = broker.publisher("pong")
    publisher_pong = broker.publisher("pong")


    @app.on_startup
    async def setup(context: ContextRepo, env: str = ".env"):
        print("setup pac0 service ...")
        settings = SettingsService(_env_file=env)
        context.set_global("settings", settings)


    @broker.subscriber("ping")
    async def ping(message):
        await publisher_pong.publish("Hi!", correlation_id=message.correlation_id)

    return broker, app


def get_nats_url():
    url = os.environ.get("NATS_URL", "nats://localhost:4222")
    print(f"Connecting to NATS {url} ...")
    return url


# ====================================================================
# common esb service features (must be included in each service)

router = NatsRouter(prefix="")

broker = None


@router.subscriber("healthcheck")
async def healthcheck_sub(
    # message: Incoming,
    # logger: Logger,
):
    # logger.info("Incoming value: %s, depends value: %s" % (message.m, dependency))
    await broker.publish("I am alive !", "healthcheck_resp")
