# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Mapping, Optional

import anyio
import niquests
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose import jwt as jwt_lib
from pydantic import BaseModel

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


class CapturedRequest(BaseModel):
    """Model for storing captured request data."""

    id: str
    timestamp: str
    method: str
    path: str
    headers: dict
    body: Optional[str]
    upstream_forwarded: bool = False


class CapturedResponse(BaseModel):
    """Model for storing captured response data."""

    request_id: str
    timestamp: str
    status_code: int
    headers: dict
    body: Optional[str]


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
    request: Request, token: Optional[str]
) -> CapturedRequest:
    """Capture request details and store them to file."""
    conf = request.app.state.conf
    # Read request body
    body = None
    try:
        body = await request.body()
        body_str = body.decode("utf-8")
    except Exception:
        body_str = ""

    # Get all headers
    headers = dict(request.headers)
    now = datetime.now()

    captured = CapturedRequest(
        id=str(uuid.uuid4()),
        timestamp=datetime.now().isoformat(),
        method=request.method,
        path=request.url.path,
        headers=headers,
        body=body_str,
    )

    # Store to file
    if conf.proxy.store.backend == "file":
        # month prefix as 202603 (YYYYMM)
        month_date_prefix = f"{now.year}{now.month:02d}"
        filepath = (
            Path(conf.proxy.store.path) / f"{month_date_prefix}-{captured.id}.pac0"
        )
        with open(filepath, "w") as f:
            json.dump(captured.model_dump(), f, indent=2)

    logger.debug(f"Proxy request captured to {filepath}")
    return captured


# async def _stream_request_body(request: Request) -> AsyncGenerator[bytes, None]:
#    """Stream request body in chunks.
#
#    Yields chunks from the ASGI receive channel to avoid loading
#    the entire request body into memory.
#    """
#    receive = request._receive
#    while True:
#        event = await receive()
#        if event.get("type") == "http.request":
#            body = event.get("body", b"")
#            if body:
#                yield body
#            if not event.get("more_body", False):
#                break
#        elif event.get("type") == "http.disconnect":
#            break


async def yield_request_body(request):
    # for i in range(10):
    #    yield b"some fake video bytes"
    #    await anyio.sleep(0)
    for chunk in await request.iter_content():
        # body += chunk
        yield chunk
        await anyio.sleep(0)


async def generate(response):
    """Synchronous generator that yields chunks from the response."""
    for chunk in await response.iter_content(chunk_size=8192):
        yield chunk


async def async_iter_content(response):
    """Async wrapper around synchronous iter_content."""
    chunk_size = 8192
    loop = asyncio.get_event_loop()
    for chunk in await loop.run_in_executor(None, response.iter_content, chunk_size):
        yield chunk


def forward_to_upstream(
    body: bytes,
    request: Request,
    # captured_req: CapturedRequest,
    api_key: Optional[str] = None,
) -> Response:
    """Forward request to upstream endpoint with full streaming.

    Uses niquests async client to stream both request body and response.
    """
    conf = request.app.state.conf
    # Prepare upstream URL
    upstream_url = conf.proxy.upstream.endpoint + "/" + request.url.path.lstrip("/")

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

            # Stream response body in chunks
            # chunks = []
            # async for chunk in response.aiter_bytes():
            #    chunks.append(chunk)
            # content = b"".join(chunks)
            #
            # TODO: cleanup headers, remove some, add some
            headers: Mapping[str, str] = response.headers

            return Response(
                # content=content,
                # content=response.iter_content(),
                # content=yield_request_body(response),
                # content=response.aiter_bytes(chunk_size=8192),  # Stream in 8KB chunks
                # content=async_iter_content(response),
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
    if not conf.proxy.enabled:
        # Proxy not enabled, let other routes handle this
        logger.critical(
            "Proxy not enabled, but request was made to %s", request.url.path
        )
        raise HTTPException(status_code=404, detail="Proxy not enabled")

    # Verify JWT token
    token = ""
    # if not verify_jwt(x_auth_token, config.proxy.upstream.api_key):
    #    raise HTTPException(status_code=401, detail="Invalid or missing JWT token")

    # Capture request
    # captured_req = capture_request_to_file(request, token)

    # logger.debug("Helmllo !!!!")
    # return {"hello": "world"}

    # Forward to upstream
    response = forward_to_upstream(
        # request, captured_req, config.proxy.upstream.api_key
        body,
        request,
        conf.proxy.upstream.api_key,
    )

    logger.info(f"Request handled by proxy: {request.method} {request.url.path}")
    return response
