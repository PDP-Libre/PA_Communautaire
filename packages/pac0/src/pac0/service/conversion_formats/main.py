# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pac0.shared.esb import init_esb_app


ctx, broker, app = init_esb_app("conversion-formats")


@broker.subscriber(ctx.subject_in, ctx.queue)
async def process(message):
    #TODO: faire qq chose ...

    # BAD: company / facture / fichier
    get_file("/334/4444/facture.xml")

    # BAD: facture / fichier  (company est déduit du JWT)
    get_file("4444/facture.xml")

    await ctx.publisher_out.publish(message)
