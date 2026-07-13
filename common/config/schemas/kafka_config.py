from pydantic import Field

from common.config.schemas.base_enum_model import BaseEnumModel
from common.config.schemas.kafka_topics_config import KafkaTopicsConfig
from common.config.schemas.tls_config import TlsConfig


class KafkaConfig(BaseEnumModel):
    bootstrap_servers: str
    consumer_group: str
    dead_letter_topic: str
    max_retries: int = Field(ge=0)
    retry_delay_seconds: float = Field(gt=0)
    topics: KafkaTopicsConfig
    tls: TlsConfig
