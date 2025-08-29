from pydantic import Field

from common.config.schemas.BaseEnumModel import BaseEnumModel


class GrpcConfig(BaseEnumModel):
    target: str = Field(default="${GRPC_TARGET}")
    credentials: str | None = Field(default=None)
    timeout: float = Field(default=5.0)

    @property
    def is_secure(self) -> bool:
        return self.credentials is not None
