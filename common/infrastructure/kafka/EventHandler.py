from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from common.infrastructure.kafka.schemas.BaseKafkaEvent import BaseKafkaEvent


@dataclass
class EventHandler:
    topic: str
    event_mapping: type[BaseKafkaEvent]
    handler: Callable[[BaseKafkaEvent], Awaitable[None]]
