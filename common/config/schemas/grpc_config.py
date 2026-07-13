from pydantic import Field

from common.config.schemas.base_enum_model import BaseEnumModel
from common.config.schemas.tls_config import TlsConfig


class GrpcConfig(BaseEnumModel):
    target: str = Field(default="localhost:9090")
    timeout: float = Field(default=5.0)
    tls: TlsConfig = Field(default_factory=TlsConfig)
