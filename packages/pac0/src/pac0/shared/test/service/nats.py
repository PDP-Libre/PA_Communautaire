from pac0.shared.test.service.base import BaseServiceContext, ServiceConfig


class NatsServiceContext(BaseServiceContext):
    """Test context for a NATS service."""

    def __init__(
        self,
        name: str | None = None,
    ) -> None:
        config = ServiceConfig(
            name=name,
            command=["uv", "fastapi", "dev", "app1/main.py"],
            port=0,
            allow_ConnectionRefusedError=True,
            health_check_path=None,
        )
        super().__init__(config)
