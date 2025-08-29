import asyncio

from aiokafka import AIOKafkaConsumer

from common.config.schemas.KafkaConfig import KafkaConfig
from common.kafka.EventHandler import EventHandler
from common.logic.grpc.GrpcClient import GrpcClient
from common.logic.utils import get_logger_from_filepath


class GlobalConsumer:
    __topics: tuple[str] = (
        "private.integration.accountlinkage",
        "private.integration.notifications",
        "private.auth.otp",
    )
    __logger = get_logger_from_filepath(__file__)
    __consumer: AIOKafkaConsumer

    __event_handlers: list[EventHandler] = []

    def __init__(self, kafka_config: KafkaConfig, grpc_client: GrpcClient):
        self.__integration_service = grpc_client
        self.config = kafka_config

    def register_handler(self, event_handler: EventHandler):
        assert event_handler.topic in self.__topics
        self.__event_handlers.append(event_handler)

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
            event_handler: EventHandler | None = self.__get_event_handler(msg.topic)
            if event_handler is None:
                self.__logger.error("No event mapper for msg in topic: {}", msg.topic)
                continue
            try:
                await event_handler.handler(
                    event_handler.event_mapping.model_validate_json(msg.value)
                )
            except Exception as e:
                self.__logger.error(
                    "Error occurred while processing kafka event: %s", e
                )

    async def stop(self):
        await self.__consumer.stop()

    def __get_event_handler(self, topic: str) -> EventHandler | None:
        for handler in self.__event_handlers:
            if handler.topic != topic:
                continue
            return handler
        return None
