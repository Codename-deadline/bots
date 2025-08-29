from common.kafka.enums.TimeRemaining import TimeRemaining
from common.kafka.schemas.BaseKafkaEvent import BaseKafkaEvent
from datetime import datetime

from common.logic.enums import Language


class DeadlinePayload(BaseKafkaEvent):
    id: int
    title: str
    due: datetime


class NotificationEvent(BaseKafkaEvent):
    chat_id: int
    language: Language
    deadline: DeadlinePayload
    timeRemaining: TimeRemaining
