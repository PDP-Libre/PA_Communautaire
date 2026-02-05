# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import os
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Request, UploadFile
from faststream.nats import NatsBroker
from pac0.service.api_gateway.lib import trace
from pac0.service.api_gateway.lib.common import broker, global_state
from pac0.shared.subjects import *
from pac0.service.api_gateway.lib.models import MsgApiFlowsOutPayload
from pac0.shared.payload import (
    VERSION,
    get_token_optional,
    get_token_required,
    flow_id_new,
)
from . import store

router = APIRouter()


@router.get("/")
async def read_root():
    return {"Hello": "World"}


@router.post("/v1/flows")
@router.post("/flows")
async def flows_post(
    broker: Annotated[NatsBroker, Depends(broker)],
    trackingId: str | None,
    sha256: str | None,
    # la facture déposée
    file: UploadFile = File(...),
    # L'authentification JWT est facultative pour cet appel
    # un autre PA peut nous appeler sans jwt
    jwt: str = Depends(get_token_optional),
):
    """
    La route POST /flows, de l’API publiée par le Fournisseur API doit permettre de déposer :
    •Une facture constituée dans un format du socle (Syntaxe CII, UBL, Factur-X)
    •Un cycle de vie sur une facture (Syntaxe CDAR)
    •Une transmission de données de E-Reporting (Syntaxe FRR pour FRench Reporting)
    •Un cycle de vie sur une transmission de données de E-reporting (Syntaxe CDAR)
    Le body de la route POST/ Flows est un multi-part composé d’un objet ‘flowInfo’ et d’un fichier binaire.
    """
    # calcule le hash sha256 de la facture déposée
    upload_hash = await store.compute_h256(file)

    if sha256 and upload_hash != sha256:
        #TODO: renvoyer une erreur HTTP
        raise Exception('hash mismatch')

    # où stocker la facture déposée
    srv, bucket, file_key = store.get_srv_bucket_key_from_file_ctx(
        hash=upload_hash,
        # le token jwt est peut-être vide
        jwt=jwt,
        # à ce moment, on ne connait ni l'utilisateur,
        # ni le fournisseur, ni le client
        user_id=None,
        supplier_id=None,
        customer_id=None,
    )

    # on pre-calcule l'URL signé pour stocker la facture (utilisé plus bas)
    store_post_presigned_url = await store.get_presigned_url(
        s3=srv,
        bucket=bucket,
        key=file_key,
        method="put_object",
    )
    # on pre-calcule l'URL signé pour récupérer la facture (utilisé par d'autres briques)
    store_get_presigned_url = await store.get_presigned_url(
        s3=srv,
        bucket=bucket,
        key=file_key,
        method="get_object",
    )

    # upload the file to s3
    await store.put(store_post_presigned_url, file)

    flow_id = await flow_id_new()
    await broker.publish(
        MsgApiFlowsOutPayload(
            version=VERSION,
            flow_id=flow_id,
            jwt=jwt,
            store_presigned_url=store_get_presigned_url,
            upload_hash=upload_hash,
            upload_filename=file.filename,
        ),
        SUBJECT_01_OUT,
    )

    return {
        "flow_id": flow_id,
        "filename": file.filename,
    }


@router.get("/v1/flows/{flowId}")
@router.get("/flows/{flowId}")
async def flows_get(
    # On doit être authentifié pour cet appel
    jwt: str = Depends(get_token_required),
):
    return {"Hello": "World"}


@router.get("/healthcheck")

@router.get("/healthcheck")
async def healthcheck(
    request: Request,
):
    return {
        "status": "OK",
        "rank": request.app.state.rank,
    }

@router.get("/healthcheck/deep")
async def healthcheck_deep(
    request: Request,
    broker: Annotated[NatsBroker, Depends(broker)],
):
    # ping the broker
    await broker.ping(timeout=5.0)
    # ask every services how they feel
    await broker.publish("Hello, NATS!", "healthcheck")
    # wait for responses
    await asyncio.sleep(2.0)

    return {
        "status": "OK",
        "rank": request.app.state.rank,
        "healthcheck_resp": global_state["healthcheck_resp"],
    }


if trace.TESTING:

    @router.get("/trace")
    async def trace_get():
        # return {"stored_msg": stored_msg}
        return trace.stored_msg

    @router.post("/publish")
    async def publish_post(
        broker: Annotated[NatsBroker, Depends(broker)],
    ):
        # TODO: pass query args
        await broker.publish("publishing ...", "xxx")
