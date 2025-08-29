from pydantic import Field

from common.config.schemas.BaseEnumModel import BaseEnumModel


class KafkaConfig(BaseEnumModel):
    bootstrap_servers: str = Field(default="${KAFKA_BOOTSTRAP_SERVERS}")
