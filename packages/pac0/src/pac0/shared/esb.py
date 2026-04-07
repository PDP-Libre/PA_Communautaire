# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
from dataclasses import dataclass
from typing import Any

from faststream import ContextRepo, FastStream
from faststream.nats import NatsBroker, NatsRouter
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

# TODO: we will use NATS queue to have pool of instances
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
    publisher_ping = broker.publisher("ping")
    publisher_pong = broker.publisher("pong")

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

    # TODO: add on_startup behaviour to annonce the new service instance
    # @app.on_startup
    # async def setup(context: ContextRepo, env: str = ".env"):
    #    print("setup pac0 service ...")
    #    settings = SettingsService(_env_file=env)
    #    context.set_global("settings", settings)

    # You MUST return broker and app separatly
    return ctx, _broker, app


def get_nats_url():
    url = os.environ.get("NATS_URL", "nats://localhost:4222")
    logger.debug(f"Using NATS {url} ...")
    return url


# ====================================================================
# common esb service features (must be included in each service)

router = NatsRouter(prefix="")

# will be set by when you import this module
broker = None


@router.subscriber("healthcheck")
async def healthcheck_sub(
    # message: Incoming,
    # logger: Logger,
):
    """
    respond to tell the service is alive
    """
    # logger.info("Incoming value: %s, depends value: %s" % (message.m, dependency))
    await broker.publish("I am alive !", "healthcheck_resp")


@router.subscriber("ping")
async def ping(message):
    """
    respond to ping with a pong
    """
    await broker.publish("Hi!", "pong", correlation_id=message.correlation_id)
