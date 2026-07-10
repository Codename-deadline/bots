from pydantic import Field

from common.config.schemas.BaseEnumModel import BaseEnumModel
from common.config.schemas.KafkaTopicsConfig import KafkaTopicsConfig


class KafkaConfig(BaseEnumModel):
    bootstrap_servers: str = Field(default="${KAFKA_BOOTSTRAP_SERVERS}")
    topics: KafkaTopicsConfig = Field(default_factory=KafkaTopicsConfig)
