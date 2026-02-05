# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any
from pac0.shared.esb import init_esb_app
from pac0.service.annuaire_local.models import (
    MsgAnnuaireLocalInPayload,
    MsgAnnuaireLocalOutPayload,
)


ctx, broker, app = init_esb_app("annuaire-local")


# TODO: move to a sqlite readonly db fetched from nats-kv (back up in s3)
# TODO: subscribe to a 'directory_updated' message
DATABASE: dict[str, Any] = {
    # TODO: que stocker dans cet annuaire ?
    "002:12345678": {},
    "002:12345679": {},
    "002:12345680": {},
}


@broker.subscriber(ctx.subject_in, ctx.queue)
async def process(message: MsgAnnuaireLocalInPayload):
    # TODO: faire qq chose ...

    # TODO: récupérer l'identifiant de l'entreprise émétrice de la facture
    # TODO: convertir en identifiant primaire (le plus court)
    company_id = "???"

    # TODO: rechercher de la base de donnée locale
    local_directory = True

    # indiquer dans le message de retour si la société est dans la base locale
    await ctx.publisher_out.publish(
        MsgAnnuaireLocalOutPayload(
            **message.model_dump(),
            local_directory=local_directory,
        )
    )
