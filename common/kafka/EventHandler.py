from dataclasses import dataclass
from typing import Awaitable, Callable, Type

from common.kafka.schemas.BaseKafkaEvent import BaseKafkaEvent


@dataclass
class EventHandler:
    topic: str
    event_mapping: Type[BaseKafkaEvent]
    handler: Callable[[BaseKafkaEvent], Awaitable[None]]
