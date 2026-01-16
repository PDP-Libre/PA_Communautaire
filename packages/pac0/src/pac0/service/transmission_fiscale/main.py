# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pac0.shared.esb import init_esb_app


ctx, broker, app = init_esb_app("transmission-fiscale")


@broker.subscriber(ctx.subject_in, ctx.queue)
async def process(message):
    await ctx.publisher_out.publish(message, correlation_id=message.correlation_id)
    # await publisher_err.publish(message, correlation_id=message.correlation_id)
