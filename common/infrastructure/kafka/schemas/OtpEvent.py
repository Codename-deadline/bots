from common.application.enums import Language
from common.infrastructure.kafka.schemas.BaseKafkaEvent import BaseKafkaEvent


class OtpEvent(BaseKafkaEvent):
    code: str
    account_id: int
    language: Language
