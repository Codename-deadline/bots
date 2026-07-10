from pydantic import Field

from common.config.schemas.base_enum_model import BaseEnumModel
from common.config.schemas.kafka_topics_config import KafkaTopicsConfig


class KafkaConfig(BaseEnumModel):
    bootstrap_servers: str = Field(default="${KAFKA_BOOTSTRAP_SERVERS}")
    topics: KafkaTopicsConfig = Field(default_factory=KafkaTopicsConfig)
