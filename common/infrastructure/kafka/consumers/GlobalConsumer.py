import asyncio
import logging

from aiokafka import AIOKafkaConsumer

from common.config.schemas.KafkaConfig import KafkaConfig
from common.infrastructure.kafka.EventHandler import EventHandler

logger = logging.getLogger(__name__)


class GlobalConsumer:
    _consumer: AIOKafkaConsumer
    _consume_task: asyncio.Task | None

    def __init__(self, kafka_config: KafkaConfig):
        self.config = kafka_config
        self._event_handlers: dict[str, EventHandler] = {}
        self._consume_task = None

    def register_handler(self, event_handler: EventHandler):
        self._event_handlers[event_handler.topic] = event_handler

    async def start(self):
        assert self._event_handlers, "No Kafka event handlers registered"

        self._consumer = AIOKafkaConsumer(
            *self._event_handlers.keys(),
            bootstrap_servers=self.config.bootstrap_servers,
        )
        await self._consumer.start()
        self._consume_task = asyncio.create_task(self._consume_loop())

    async def _consume_loop(self):
        async for msg in self._consumer:
            event_handler: EventHandler | None = self._event_handlers.get(msg.topic)
            if event_handler is None:
                logger.error("No event mapper for msg in topic: %s", msg.topic)
                continue
            try:
                await event_handler.handler(
                    event_handler.event_mapping.model_validate_json(msg.value or "{}")
                )
            except Exception as e:
                logger.exception("Error occurred while processing kafka event: %s", e)

    async def stop(self):
        if self._consume_task is not None:
            self._consume_task.cancel()
        await self._consumer.stop()
