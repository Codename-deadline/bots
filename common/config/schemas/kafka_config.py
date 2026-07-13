from pydantic import Field

from common.config.schemas.base_enum_model import BaseEnumModel
from common.config.schemas.kafka_topics_config import KafkaTopicsConfig
from common.config.schemas.tls_config import TlsConfig


class KafkaConfig(BaseEnumModel):
    bootstrap_servers: str = Field(default="localhost:9092")
    consumer_group: str = Field(default="deadline-bots")
    dead_letter_topic: str = Field(default="private.integration.dead-letter")
    max_retries: int = Field(default=5, ge=0)
    retry_delay_seconds: float = Field(default=5.0, gt=0)
    topics: KafkaTopicsConfig = Field(default_factory=KafkaTopicsConfig)
    tls: TlsConfig = Field(default_factory=TlsConfig)
