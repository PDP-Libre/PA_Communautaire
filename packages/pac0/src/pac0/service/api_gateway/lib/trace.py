# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any
from pydantic import BaseModel

# TODO: set to False on prod
TESTING = True
MAX_TRACE = 200

class MsgInfo(BaseModel):
    body: bytes
    content_type: str
    message_id: str
    correlation_id: str
    path: dict[Any, Any]
    committed: Any | None
    subject: str
    reply: str


stored_msg: list[MsgInfo] = []

def add(msg: MsgInfo):
    del stored_msg[:-MAX_TRACE]
    stored_msg.append(msg)