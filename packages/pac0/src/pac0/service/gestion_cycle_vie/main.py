# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pac0.shared.esb import init_esb_app
from pac0.shared.subjects import *


ctx, broker, app = init_esb_app("gestion-cycle-vie")


publisher_03_IN = broker.publisher(SUBJECT_03_IN)
publisher_04_IN = broker.publisher(SUBJECT_04_IN)
publisher_05_IN = broker.publisher(SUBJECT_05_IN)
publisher_06_IN = broker.publisher(SUBJECT_06_IN)
publisher_07_IN = broker.publisher(SUBJECT_07_IN)
publisher_08_IN = broker.publisher(SUBJECT_08_IN)

publisher_err = broker.publisher(SUBJECT_09_ERR)


@broker.subscriber(SUBJECT_01_OUT, ctx.queue)
async def process_01_to_03(message):
    await publisher_03_IN.publish(message, correlation_id=message.correlation_id)


@broker.subscriber(SUBJECT_03_OUT, ctx.queue)
async def process_03_to_04(message):
    await publisher_04_IN.publish(message, correlation_id=message.correlation_id)


@broker.subscriber(SUBJECT_04_OUT, ctx.queue)
async def process_04_to_05(message):
    await publisher_05_IN.publish(message, correlation_id=message.correlation_id)


@broker.subscriber(SUBJECT_05_OUT, ctx.queue)
async def process_05_to_06(message):
    await publisher_06_IN.publish(message, correlation_id=message.correlation_id)


@broker.subscriber(SUBJECT_06_OUT, ctx.queue)
async def process_06_to_07(message):
    # TODO: ne faire le routage que si non présent dans l'annuaire
    # TODO: trouver `dans_annuaire_local` dans `message`
    dans_annuaire_local = True
    # soit on passe à 07 ou à 08
    next_publisher = publisher_07_IN if not dans_annuaire_local else publisher_08_IN
    await next_publisher.publish(message, correlation_id=message.correlation_id)


@broker.subscriber(SUBJECT_07_OUT, ctx.queue)
async def process_07_to_08(message):
    await publisher_08_IN.publish(message, correlation_id=message.correlation_id)


@broker.subscriber(SUBJECT_01_ERR, ctx.queue)
@broker.subscriber(SUBJECT_02_ERR, ctx.queue)
@broker.subscriber(SUBJECT_03_ERR, ctx.queue)
@broker.subscriber(SUBJECT_04_ERR, ctx.queue)
@broker.subscriber(SUBJECT_05_ERR, ctx.queue)
@broker.subscriber(SUBJECT_06_ERR, ctx.queue)
@broker.subscriber(SUBJECT_07_ERR, ctx.queue)
@broker.subscriber(SUBJECT_08_ERR, ctx.queue)
async def process_err(message):
    # TODO: common err behaviour
    ...
