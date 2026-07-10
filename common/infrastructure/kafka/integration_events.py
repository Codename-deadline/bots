from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from common.config.schemas.KafkaConfig import KafkaConfig
from common.infrastructure.kafka.consumers.GlobalConsumer import GlobalConsumer
from common.infrastructure.kafka.EventHandler import EventHandler
from common.infrastructure.kafka.schemas.AccountLinkageEvent import AccountLinkageEvent
from common.infrastructure.kafka.schemas.NotificationEvent import NotificationEvent
from common.infrastructure.kafka.schemas.OtpEvent import OtpEvent


@dataclass(frozen=True)
class IntegrationEventHandlers:
    account_linkage: Callable[[AccountLinkageEvent], Awaitable[None]]
    notifications: Callable[[NotificationEvent], Awaitable[None]]
    otp: Callable[[OtpEvent], Awaitable[None]]


def build_integration_consumer(
    kafka_config: KafkaConfig, handlers: IntegrationEventHandlers
) -> GlobalConsumer:
    consumer = GlobalConsumer(kafka_config)
    consumer.register_handler(
        EventHandler(
            kafka_config.topics.account_linkage,
            AccountLinkageEvent,
            handlers.account_linkage,
        )
    )
    consumer.register_handler(
        EventHandler(
            kafka_config.topics.notifications,
            NotificationEvent,
            handlers.notifications,
        )
    )
    consumer.register_handler(
        EventHandler(kafka_config.topics.otp, OtpEvent, handlers.otp)
    )
    return consumer
