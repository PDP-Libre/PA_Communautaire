# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import time
from pydantic import BaseModel
from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

VERSION = 1

class MsgPayloadBase(BaseModel):
    '''
    All message payload inherit from this base model
    '''
    # version des messages
    version: int = 1
    # the unique flow id
    flow_id: int
    # JWT token as given in the API entry point
    jwt: str | None



dummy_inc = int(time.time())*100_000
async def flow_id_new():
    '''
    Return a new flow id
    TODO: based on what ? user/company/year-month/pa ?
    '''
    global dummy_inc
    #TODO: inc a nats KV 
    dummy_inc += 1
    return dummy_inc


security = HTTPBearer(auto_error=False)  # auto_error=False for flexibility


async def get_token_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    """Get token from multiple sources without raising errors"""
    # 1. HTTP Bearer header
    if credentials and credentials.scheme.lower() == "bearer":
        return credentials.credentials

    # 2. Query parameter
    token = request.query_params.get("access_token")
    if token:
        return token

    # 3. Cookie
    token = request.cookies.get("access_token")
    if token:
        return token

    return None

async def get_token_required(token: Optional[str] = Depends(get_token_optional)) -> str:
    """Require a valid token"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token"
        )
    return token
