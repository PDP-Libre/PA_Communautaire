"""


Example of a CLI query with *real* data:

❯ dig -t NAPTR +short 54VMPCQA26DNZS74VHQOKJ7U6IRBBI5KPMQ6AO3KVCQC3F6YR2YA.iso6523-actorid-upis.de4a.edelivery.tech.ec.europa.eu
100 10 "U" "Meta:SMP" "!.*!https://de4a-smp.usp.gv.at!" .


❯ dig @127.0.0.1 -p 5353 -t NAPTR +short 54VMPCQA26DNZS74VHQOKJ7U6IRBBI5KPMQ6AO3KVCQC3F6YR2YA.iso6523-actorid-upis.de4a.edelivery.tech.ec.europa.eu
"""

from pac0.shared.test.service.base import BaseServiceContext, ServiceConfig


class DNSServiceContext(BaseServiceContext):
    """Test context for a DNS service."""

    def __init__(self) -> None:
        config = ServiceConfig(
            name = "peppol",
            command=["uv", "run", "src/pac0/service/peppol_dns_fake/main.py"],
            port=0,
            allow_ConnectionRefusedError = True,
            health_check_path = None,
        )
        super().__init__(config)
