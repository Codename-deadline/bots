from common.config.schemas.base_enum_model import BaseEnumModel
from common.config.schemas.kafka_topics_config import KafkaTopicsConfig


class KafkaConfig(BaseEnumModel):
    bootstrap_servers: str
    topics: KafkaTopicsConfig
