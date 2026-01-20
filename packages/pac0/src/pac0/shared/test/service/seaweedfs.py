# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""

cf quickstart : https://github.com/seaweedfs/seaweedfs?tab=readme-ov-file#quick-start-with-weed-mini



This single command starts a complete SeaweedFS setup with:

    Master UI: http://localhost:9333
    Volume Server: http://localhost:9340
    Filer UI: http://localhost:8888
    S3 Endpoint: http://localhost:8333
    WebDAV: http://localhost:7333
    Admin UI: http://localhost:23646

"""
from tempfile import TemporaryDirectory
from pac0.shared.test.service.base import BaseServiceContext, ServiceConfig
from dataclasses import dataclass


@dataclass
class SeaweedfsServiceConfig(ServiceConfig):
    data_dir: str | TemporaryDirectory
    port_master_ui: int = 9333
    port_volume_server: int = 9340
    port_filer_ui: int = 8888
    port_s3_endpoint: int = 8333
    port_webdav: int = 7333
    port_admin_ui: int = 23646

class SeaweedfsServiceContext(BaseServiceContext):
    """Test context for a SeaweedFS service."""

    def __init__(
        self,
        name: str = "seaweedfs",
        data_dir: str | TemporaryDirectory | None = None,
    ) -> None:
        if data_dir is None:
            data_dir = TemporaryDirectory()

        config = SeaweedfsServiceConfig(
            name=name,
            # weed mini -webdav=false -dir=/tmp/data
            # weed server -dir=/tmp/data -s3 -s3.port=9000 -master.port=0 -volume.port=0 -filer.port=0 -metrics.port=0
            # weed server -s3 -s3.port=8333 -ip=0.0.0.0 -volume.max=0 -master.volumeSizeLimitMB=1024 -master.port=0 -volume.port=0 -filer.port=0
            command=[
                "weed",
                "mini",
                f"-dir={data_dir}",
            ],
            port=0,
            allow_ConnectionRefusedError=True,
            health_check_path="/",
            data_dir=data_dir,
        )
        super().__init__(config)

