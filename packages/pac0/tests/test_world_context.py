# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import pytest
from unittest.mock import patch, AsyncMock

from pac0.shared.test.service.pac import PacServiceContext
from pac0.shared.test.service.fastapi import FastApiServiceContext
from pac0.shared.test.service.base import BaseServiceContext, ServiceConfig
from pac0.shared.test.world import WorldContext, world, world1

# logging.getLogger().setLevel('DEBUG')


async def test_world_with_0pa():
    """Default WorldContext has no PA."""
    async with WorldContext() as world:
        assert len(world.pas) == 0


async def test_world_with_1pa_default():
    """WorldContext with 1 PA instance."""
    async with WorldContext() as world:
        await world.pa_new()  # default is 1
        assert len(world.pas) == 1


async def test_world_with_1pa():
    async with WorldContext() as world:
        await world.pa_new(1)
        assert len(world.pas) == 1


async def test_world_with_4pa():
    """WorldContext with 4 PA instances."""
    async with WorldContext() as world:
        await world.pa_new(4)
        assert len(world.pas) == 4


async def test_pac_ctx():
    """pac service context"""
    async with PacServiceContext():
        ...


async def test_brique_01_ctx1():
    """service ephémère"""
    async with FastApiServiceContext() as svc:
        assert svc.config.port != 0


async def test_brique_01_ctx2():
    """service localhost absent"""
    with pytest.raises(TimeoutError):
        async with FastApiServiceContext(external_svc="http://localhost:4588"):
            assert False, "You Shall Not Pass !"


async def test_brique_01_ctx3():
    """service localhost présent"""
    # start an ephemeral service
    async with FastApiServiceContext() as svc1:
        # get the port
        port = svc1.config.port
        external_svc = f"http://localhost:{port}"

        # use it as an external service
        async with FastApiServiceContext(external_svc=external_svc):
            ...


async def test_brique_01_ctx4():
    """service localhost présent envar"""
    # start an ephemeral service
    async with FastApiServiceContext() as svc1:
        # get the port
        port = svc1.config.port
        external_svc = f"http://localhost:{port}"

        with patch.dict(os.environ, {"PAC0_API_URL": external_svc}):
            # use it as an external service
            async with FastApiServiceContext():
                ...


async def test_brique_01_ctx5():
    """service localhost absent envar"""
    with patch.dict(os.environ, {"PAC0_API_URL": "http://localhost:4588"}):
        with pytest.raises(TimeoutError):
            async with FastApiServiceContext():
                ...


async def test_base_svc_ctx():
    """
    service base ephémère
    Démarre un service api sur un port aléatoire
    """
    cfg = ServiceConfig(
        command=[
            "uv",
            "run",
            "fastapi",
            "run",
            "--port={PORT}",
            "tests/dummy.py",
        ],
        port=0,
        health_check_path="/alive",
    )
    async with BaseServiceContext(cfg) as svc:
        assert svc.config.port != 0


async def test_base_svc_var():
    """
    service base externe env var vide
    le service extérieur est indiqué par la varianble d'environnement PAC0_DUMMY_SERVICE
    la variable d'environnement n'étant pas défini, le service est lancé par le test
    """
    cfg = ServiceConfig(
        command=[
            "uv",
            "run",
            "fastapi",
            "run",
            "--port={PORT}",
            "tests/dummy.py",
        ],
        port=0,
        health_check_path="/alive",
        env_var="PAC0_DUMMY_SERVICE",
    )
    async with BaseServiceContext(cfg):
        ...


async def test_base_svc_var_ko():
    """
    service base externe env var incorrecte
    le service extérieur est indiqué par la varianble d'environnement PAC0_DUMMY_SERVICE
    la variable d'environnement indique un service absent donc on échoue
    """
    cfg = ServiceConfig(
        command=[
            "uv",
            "run",
            "fastapi",
            "run",
            "--port={PORT}",
            "tests/dummy.py",
        ],
        port=0,
        health_check_path="/alive",
        env_var="PAC0_DUMMY_SERVICE",
    )
    with patch.dict(os.environ, {"PAC0_DUMMY_SERVICE": "http://localhost:4588"}):
        with pytest.raises(TimeoutError):
            async with BaseServiceContext(cfg):
                ...


async def test_base_svc_var_ok():
    """
    service base externe env var valide
    le service extérieur est indiqué par la varianble d'environnement PAC0_DUMMY_SERVICE
    la variable d'environnement indique un service valide
    """
    cfg = ServiceConfig(
        command=[
            "uv",
            "run",
            "fastapi",
            "run",
            "--port={PORT}",
            "tests/dummy.py",
        ],
        port=0,
        health_check_path="/alive",
        env_var="PAC0_DUMMY_SERVICE",
    )
    # start an ephemeral service
    async with BaseServiceContext(cfg) as svc1:
        # get the port
        port = svc1.config.port
        external_svc = f"http://localhost:{port}"

        with patch.dict(os.environ, {"PAC0_DUMMY_SERVICE": external_svc}):
            async with BaseServiceContext(cfg):
                ...


def test_fixture_world1(
    world1: WorldContext,
):
    """
    fixture world1
    Expose sous forme de `fixture` un context pac complet
    avec tous les services lancés
    """
    ...