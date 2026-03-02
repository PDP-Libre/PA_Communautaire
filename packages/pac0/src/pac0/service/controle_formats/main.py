# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pac0.service.controle_formats.models import (
    MsgControleFormatsInPayload,
    MsgControleFormatsOutPayload,
)
from pac0.shared.esb import CtxService, init_esb_app


# @broker.subscriber(ctx.subject_in, ctx.queue)
async def process(
    ctx: CtxService,
    message: MsgControleFormatsInPayload,
):
    """
    Le fichier uploadé est probablement non identifié à ce stade.
    Determiner son format et en vérifier la cohérence.
    Extraire de ce format les infos utile pour déplacer le fichier
    Déplacer le fichier au bon endroit
    """
    await ctx.publisher_out.publish(
        MsgControleFormatsOutPayload(**message.model_dump())
    )


ctx, broker, app = init_esb_app("controle-formats", process=process)
