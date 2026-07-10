from datetime import datetime

from common.application.enums import Language
from common.infrastructure.kafka.enums.time_remaining import TimeRemaining
from common.infrastructure.kafka.schemas.base_kafka_event import BaseKafkaEvent


class DeadlinePayload(BaseKafkaEvent):
    id: int
    title: str
    due: datetime


class NotificationEvent(BaseKafkaEvent):
    chat_id: int
    language: Language
    deadline: DeadlinePayload
    timeRemaining: TimeRemaining
