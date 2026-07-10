from common.application.enums import Language
from common.infrastructure.kafka.schemas.base_kafka_event import BaseKafkaEvent


class OtpEvent(BaseKafkaEvent):
    code: str
    account_id: int
    language: Language
