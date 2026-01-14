# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import random
import socket
from contextlib import asynccontextmanager, closing
from typing import AsyncGenerator

import uvicorn


# semaphore to allow only one port test at a time
semaphore_sock_bind = asyncio.Semaphore(1)


PORT_START = 8300
PORT_END = 9300
_ports_to_try = [*range(PORT_START, PORT_END)]
random.shuffle(_ports_to_try)


async def find_available_port(
    start_port: int = 8200,
    max_attempts: int = 500,
) -> int:
    """
    Find an available port starting from a random port within a range.

    Args:
        start_port: Minimum port number to start searching from
        max_attempts: Maximum number of ports to check

    Returns:
        Available port number
    """
    while len(_ports_to_try) > 0:
        port = _ports_to_try.pop()

        # Try to bind to the port to check if it's available
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            # Set SO_REUSEADDR to allow reuse of the port
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                async with semaphore_sock_bind:
                    # Try to bind to the port
                    sock.bind(("0.0.0.0", port))
                    # Port is available
                    return port
            except OSError as e:
                # Port is in use
                pass

    raise Exception("no port available")


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
        port = await find_available_port()

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
