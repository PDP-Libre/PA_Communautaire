# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import json
import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Mapping, Optional

import anyio
import niquests
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose import jwt as jwt_lib

from pac0.service.api_gateway.config import Settings

logger = logging.getLogger(__name__)

router = APIRouter()


def print_banner(conf: Settings):
    print(rf"""
_______________________________________
__________________ ________/ __ \
_______/ __ \/ __ `// ___// / / /
______/ /_/ / /_/ // /__ / /_/ /
_____/ .___/\__,_/ \___/ \____/
____/_/       ░░░█▀█░█▀▄░█▀█░█░█░█░█░░░
              ░░░█▀▀░█▀▄░█░█░▄▀▄░░█░░░░
              ░░░▀░░░▀░▀░▀▀▀░▀░▀░░▀░░░░

  PA: {conf.proxy.upstream.endpoint}

  🇫🇷 🇪🇺 facturation électronique
  plateforme agréée communautaire
_______________________________________
""")

    if conf.proxy.store.backend == "file":
        path = Path(conf.proxy.store.path)
        path.mkdir(parents=True, exist_ok=True)


def get_jwt_token(x_auth_token: Optional[str] = None) -> Optional[str]:
    """Extract JWT token from request headers."""
    if x_auth_token:
        return x_auth_token

    # Also check Authorization header
    # This would need to be passed from the main request
    return None


def verify_jwt(token: str, api_key: Optional[str] = None) -> bool:
    """Verify JWT token if authentication is required."""
    if not token:
        return False

    # TODO: Add your JWT secret key via environment variable (e.g., PAC0_PROXY_JWT_SECRET)
    # and properly verify the signature
    # Example: JWT_SECRET = os.getenv("PAC0_PROXY_JWT_SECRET", "")
    # return jwt_lib.decode(token, JWT_SECRET, algorithms=["HS256"])

    # For now, we'll just check if token exists (insecure for production!)
    try:
        # Decode without verification for now (requires proper secret)
        payload = jwt_lib.decode(token, options={"verify_signature": False})
    except Exception as e:
        logger.error(f"Proxy request auth failed: {e}")
        return False

    logger.debug(f"Proxy request auth accepted {payload=}")
    return True


async def capture_request_to_file(
    request: Request,
    response,
    token: Optional[str],
    start_time: datetime,
):
    """Capture request details and store them to file."""
    conf = request.app.state.conf
    # Read request body
    body = None
    try:
        body = await request.body()
        body_str = body.decode("utf-8")
    except Exception:
        body_str = ""

    now = datetime.now()
    row_id = str(uuid.uuid4())

    # Store to file
    if conf.proxy.store.backend == "file":
        # month prefix as 202603 (YYYYMM)
        month_date_prefix = f"{now.year}{now.month:02d}"
        filepath = Path(conf.proxy.store.path) / f"{month_date_prefix}-{row_id}.pac0"
        with open(filepath, "w") as f:
            json.dump(
                {
                    "id": row_id,
                    "m": "N/A",
                    "t": start_time,
                    "v": request.method,
                    "e": conf.proxy.upstream.endpoint,
                    "p": request.url.path,
                    "s": response.status_code,
                    #'d': int((datetime.now() - start_time).total_seconds() * 1000),
                    "req": {
                        # TODO: calculate sha256 and length while proxying
                        "size": len(await request.body()),
                        "sha256": "N/A",
                    },
                    "res": {
                        # TODO: calculate sha256 and length while proxying
                        "size": "N/A",
                        "sha256": "N/A",
                    },
                },
                f,
                indent=2,
            )
        logger.debug(f"Proxy request captured to {filepath}")


async def async_iter_content(response):
    """Async wrapper around synchronous iter_content."""
    chunk_size = 8192
    loop = asyncio.get_event_loop()
    for chunk in await loop.run_in_executor(None, response.iter_content, chunk_size):
        yield chunk


def forward_to_upstream(
    body: bytes,
    request: Request,
    api_key: Optional[str] = None,
) -> Response:
    """Forward request to upstream endpoint with full streaming.

    Uses niquests async client to stream both request body and response.
    """
    conf = request.app.state.conf
    # Prepare upstream URL
    upstream_url = conf.proxy.upstream.endpoint + "/" + request.url.path.lstrip("/")

    logger.debug(f"Preparing upstream query {request.method} {upstream_url} ...")

    # Prepare headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header

    # Add API key if configured
    if api_key:
        headers["x-api-key"] = api_key

    # Create niquests client and forward with streaming
    # async with niquests.AsyncSession() as client:
    with niquests.Session() as s:
        try:
            response = s.request(
                method=request.method,
                url=upstream_url,
                headers=headers,
                # data=_stream_request_body(request),  # Stream body chunks
                # data=request.stream(),
                data=body,
                # TODO: move to conf
                timeout=30.0,
                stream=True,  # Enable streaming response
            )

            # Update captured request
            # captured_req.upstream_forwarded = True
            logger.debug(
                f"Proxy upstream response received: {request.method} {request.url.path}"
            )

            # TODO: cleanup headers, remove some, add some
            headers: Mapping[str, str] = response.headers

            return Response(
                content=response.content,
                status_code=response.status_code or 400,
                headers=headers,
            )
        except Exception as e:
            logger.error(
                f"Proxy upstream response failed: {request.method} {request.url.path}, {e}"
            )
            raise HTTPException(status_code=502, detail=f"Upstream error: {str(e)}")


async def get_body(request: Request):
    """Async dependency to read and return the request body."""
    return await request.body()


@router.get("/health")
async def proxy_health():
    """Health check for proxy endpoint."""
    return {
        "status": "alive",
    }


# keep it synchronous so fastapi will use the thread pool executor
# keep in last position so it doesn't override other routes
@router.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
)
def proxy_all(
    request: Request,
    path: str = "",
    body: bytes = Depends(get_body),
    # x_auth_token: Optional[str] = Header(None),
):
    """
    Catch all proxy endpoint (not empty and not already defined) and:
    1. Checks JWT token
    2. Captures all requests to files
    3. Forwards requests to upstream endpoint
    """
    conf = request.app.state.conf
    start_time = datetime.now()

    # Verify JWT token
    token = ""
    # if not verify_jwt(x_auth_token, config.proxy.upstream.api_key):
    #    raise HTTPException(status_code=401, detail="Invalid or missing JWT token")

    # logger.debug("Helmllo !!!!")
    # return {"hello": "world"}

    # Forward to upstream
    response = forward_to_upstream(
        # request, captured_req, config.proxy.upstream.api_key
        body,
        request,
        conf.proxy.upstream.api_key,
    )

    # Capture request
    captured_req = capture_request_to_file(request, response, token, start_time)
    #
    logger.info(f"Request handled by proxy: {request.method} {request.url.path}")
    return response
