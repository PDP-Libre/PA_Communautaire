import asyncio
import random
import socket
from contextlib import asynccontextmanager, closing
from typing import AsyncGenerator

import uvicorn


def find_available_port(
    start_port: int = 8200,
    max_attempts: int = 200,
) -> int:
    """
    Find an available port starting from a random port within a range.

    Args:
        start_port: Minimum port number to start searching from
        max_attempts: Maximum number of ports to check

    Returns:
        Available port number
    """
    # Start from a random port to avoid collisions
    port = random.randint(start_port, start_port + max_attempts)

    for _ in range(max_attempts):
        # Try to bind to the port to check if it's available
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            # Set SO_REUSEADDR to allow reuse of the port
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                # Try to bind to the port
                sock.bind(("0.0.0.0", port))
                # Port is available
                return port
            except OSError:
                # Port is in use, try the next one
                port += 1
                # Wrap around if we exceed max range
                if port > 65535:
                    port = start_port

    # Fallback to a default port if none found
    return start_port


@asynccontextmanager
async def uvicorn_context(
    app,
    host: str = "127.0.0.1",
    port: int = 8543,
    **uvicorn_kwargs,
) -> AsyncGenerator[uvicorn.Server, None]:
    """
    Async context manager for Uvicorn server
    set port=0 for a random port
    """
    if port == 0:
        port = find_available_port()

    config = uvicorn.Config(app=app, host=host, port=port, **uvicorn_kwargs)
    server = uvicorn.Server(config)

    # Start server in background thread
    server_task = asyncio.create_task(server.serve())

    # Wait for server to start
    while not server.started:
        await asyncio.sleep(0.1)

    try:
        yield server
    finally:
        # Graceful shutdown
        server.should_exit = True
        await server_task
