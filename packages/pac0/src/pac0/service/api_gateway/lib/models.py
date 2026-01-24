# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pac0.shared.payload import MsgPayloadBase


class MsgApiFlowsOutPayload(MsgPayloadBase):
    # a pre-signed s3 url to read the initial file
    store_presigned_url: str
    #TODO: handle other pre-signed url depending of the 'brique'
    # the sha256 hash of the uploaded initial file
    upload_hash: str
    # the filename of the uploaded initial file
    upload_filename: str
