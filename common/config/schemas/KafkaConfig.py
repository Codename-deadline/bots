from common.config.schemas.BaseEnumModel import BaseEnumModel
from common.config.schemas.KafkaTopicsConfig import KafkaTopicsConfig


class KafkaConfig(BaseEnumModel):
    bootstrap_servers: str
    topics: KafkaTopicsConfig
