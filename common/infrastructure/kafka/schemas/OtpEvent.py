from common.kafka.schemas.BaseKafkaEvent import BaseKafkaEvent
from common.logic.enums import Language


class OtpEvent(BaseKafkaEvent):
    code: str
    account_id: int
    language: Language
