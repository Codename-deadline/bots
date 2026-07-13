from common.config.schemas.base_enum_model import BaseEnumModel
from common.config.schemas.tls_config import TlsConfig


class GrpcConfig(BaseEnumModel):
    target: str
    timeout: float
    tls: TlsConfig
