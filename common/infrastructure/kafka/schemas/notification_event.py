from datetime import datetime

from common.application.enums import Language
from common.infrastructure.kafka.enums.time_remaining import TimeRemaining
from common.infrastructure.kafka.schemas.base_kafka_event import BaseKafkaEvent


class RawEntityPayload(BaseKafkaEvent):
    id: int
    title: str


class DeadlinePayload(BaseKafkaEvent):
    id: int
    title: str
    due: datetime


class NotificationEvent(BaseKafkaEvent):
    chat_id: int
    language: Language
    organization: RawEntityPayload
    thread: RawEntityPayload
    deadline: DeadlinePayload
    timeRemaining: TimeRemaining
