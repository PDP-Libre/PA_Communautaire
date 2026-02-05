# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pac0.shared.payload import MsgPayloadBase


class MsgAnnuaireLocalInPayload(MsgPayloadBase):
    # l'identifiant court de l'entreprise
    company_id: str
    # ...
    # ...


class MsgAnnuaireLocalOutPayload(MsgPayloadBase):
    local_directory: bool
    # ...