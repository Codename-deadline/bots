from datetime import datetime

from common.application.enums import Language
from common.infrastructure.kafka.enums.TimeRemaining import TimeRemaining
from common.infrastructure.kafka.schemas.BaseKafkaEvent import BaseKafkaEvent


class DeadlinePayload(BaseKafkaEvent):
    id: int
    title: str
    due: datetime


class NotificationEvent(BaseKafkaEvent):
    chat_id: int
    language: Language
    deadline: DeadlinePayload
    timeRemaining: TimeRemaining
