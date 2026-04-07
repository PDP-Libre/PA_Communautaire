# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from jose import jwt as jwt_lib
from pydantic import BaseModel

from pac0.service.api_gateway.config import Settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/toto2")
def _():
    print("toto2")


# Configuration
config: Optional[Settings] = None


def init_config(settings: Settings):
    """Initialize the proxy router configuration."""
    global config
    config = settings


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


def ensure_storage_dir():
    """Ensure the storage directory exists."""
    if config and config.proxy.store.path:
        path = Path(config.proxy.store.path)
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
    request: Request, token: Optional[str]
) -> CapturedRequest:
    """Capture request details and store them to file."""
    # Read request body
    body = None
    try:
        body = await request.body()
        body_str = body.decode("utf-8")
    except Exception:
        body_str = ""

    # Get all headers
    headers = dict(request.headers)

    captured = CapturedRequest(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        method=request.method,
        path=request.url.path,
        headers=headers,
        body=body_str,
    )

    # Store to file
    if config and config.proxy.store.backend == "file":
        ensure_storage_dir()
        filepath = Path(config.proxy.store.path) / f"{captured.id}.json"
        with open(filepath, "w") as f:
            json.dump(captured.model_dump(), f, indent=2)

    logger.debug(f"Proxy request captured to {filepath}")
    return captured


async def forward_to_upstream(
    request: Request,
    captured_req: CapturedRequest,
    api_key: Optional[str] = None,
) -> Response:
    """Forward request to upstream endpoint."""
    if not config or not config.proxy.upstream.endpoint:
        raise HTTPException(status_code=503, detail="Upstream not configured")

    # Prepare upstream URL
    upstream_url = config.proxy.upstream.endpoint + request.url.path
    upstream_url = upstream_url.rstrip("/") + "/" + request.url.path.lstrip("/")

    # Prepare headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header

    # Add API key if configured
    if api_key:
        headers["x-api-key"] = api_key

    # Create HTTP client and forward request
    # TODO: use niquests
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=upstream_url,
                # TODO: use streaming
                headers=headers,
                content=await request.body(),
                # TODO: move to config
                timeout=30.0,
            )

            # Update captured request
            captured_req.upstream_forwarded = True
            logger.debug(
                f"Proxy upstream response received: {request.method} {request.url.path}"
            )
            # TODO: use streaming
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        except httpx.RequestError as e:
            logger.error(
                f"Proxy upstream response failed: {request.method} {request.url.path}, {e}"
            )
            raise HTTPException(status_code=502, detail=f"Upstream error: {str(e)}")


@router.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
)
async def proxy_all(
    request: Request,
    path: str = "",
    # x_auth_token: Optional[str] = Header(None),
):
    """
    Catch all proxy endpoint (not empty and not already defined) and:
    1. Checks JWT token
    2. Captures all requests to files
    3. Forwards requests to upstream endpoint
    """
    print(f"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx {path=}")

    if not config or not config.proxy.enabled:
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
    captured_req = await capture_request_to_file(request, token)

    # Forward to upstream
    response = await forward_to_upstream(
        request, captured_req, config.proxy.upstream.api_key
    )

    logger.info(f"Request handled by proxy: {request.method} {request.url.path}")
    return response


@router.get("/health")
async def proxy_health():
    """Health check for proxy endpoint."""
    if not config or not config.proxy.enabled:
        return {"status": "disabled"}

    return {
        "status": "enabled",
        "upstream": config.proxy.upstream.endpoint,
        "store_path": config.proxy.store.path,
    }
