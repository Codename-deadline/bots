import asyncio
import logging

from aiokafka import AIOKafkaConsumer

from common.config.schemas.KafkaConfig import KafkaConfig
from common.infrastructure.kafka.EventHandler import EventHandler

logger = logging.getLogger(__name__)


class GlobalConsumer:
    __topics: tuple[str] = (
        "private.integration.accountlinkage",
        "private.integration.notifications",
        "private.auth.otp",
    )
    __consumer: AIOKafkaConsumer

    def __init__(self, kafka_config: KafkaConfig):
        self.config = kafka_config
        self.__event_handlers: dict[str, EventHandler] = {}

    def register_handler(self, event_handler: EventHandler):
        assert event_handler.topic in self.__topics
        self.__event_handlers[event_handler.topic] = event_handler

    async def start(self):
        assert len(self.__event_handlers) == len(self.__topics), (
            f"Number of registered handlers does not match with number of topics:"
            f"{len(self.__event_handlers)}/{len(self.__topics)}"
        )

        self.__consumer = AIOKafkaConsumer(
            *self.__topics, bootstrap_servers=self.config.bootstrap_servers
        )
        await self.__consumer.start()
        asyncio.create_task(self.__consume_loop())

    async def __consume_loop(self):
        async for msg in self.__consumer:
            event_handler: EventHandler | None = self.__event_handlers.get(msg.topic)
            if event_handler is None:
                logger.error("No event mapper for msg in topic: %s", msg.topic)
                continue
            try:
                await event_handler.handler(
                    event_handler.event_mapping.model_validate_json(msg.value)
                )
            except Exception as e:
                logger.exception("Error occurred while processing kafka event: %s", e)

    async def stop(self):
        await self.__consumer.stop()
