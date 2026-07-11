import asyncio
import contextlib
import logging
from dataclasses import dataclass
from typing import Any

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import IllegalStateError
from aiokafka.structs import ConsumerRecord, TopicPartition
from pydantic import ValidationError

from common.config.schemas.kafka_config import KafkaConfig
from common.infrastructure.kafka.event_handler import EventHandler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class KafkaMessageKey:
    topic: str
    partition: int
    offset: int


class GlobalConsumer:
    _consumer: AIOKafkaConsumer
    _consume_task: asyncio.Task | None
    _dead_letter_producer: AIOKafkaProducer

    def __init__(self, kafka_config: KafkaConfig):
        self.config = kafka_config
        self._event_handlers: dict[str, EventHandler[Any]] = {}
        self._consume_task = None
        self._retries: dict[KafkaMessageKey, int] = {}
        self._retry_tasks: dict[TopicPartition, asyncio.Task[None]] = {}

    def register_handler(self, event_handler: EventHandler[Any]):
        self._event_handlers[event_handler.topic] = event_handler

    async def start(self):
        assert self._event_handlers, "No Kafka event handlers registered"

        self._consumer = AIOKafkaConsumer(
            *self._event_handlers.keys(),
            bootstrap_servers=self.config.bootstrap_servers,
            group_id=self.config.consumer_group,
            enable_auto_commit=False,
        )
        await self._consumer.start()
        self._dead_letter_producer = AIOKafkaProducer(
            bootstrap_servers=self.config.bootstrap_servers
        )
        await self._dead_letter_producer.start()
        self._consume_task = asyncio.create_task(self._consume_loop())

    async def _consume_loop(self):
        async for msg in self._consumer:
            event_handler: EventHandler[Any] | None = self._event_handlers.get(
                msg.topic
            )
            if event_handler is None:
                logger.error("No event mapper for msg in topic: %s", msg.topic)
                continue
            try:
                await event_handler.handler(
                    event_handler.event_mapping.model_validate_json(msg.value or "{}")
                )
            except ValidationError as error:
                await self._move_to_dead_letter(msg, error)
            except Exception as error:
                await self._retry_or_dead_letter(msg, error)
            else:
                await self._commit(msg)

    async def _retry_or_dead_letter(
        self, msg: ConsumerRecord, error: Exception
    ) -> None:
        message_key = KafkaMessageKey(msg.topic, msg.partition, msg.offset)
        attempt: int = self._retries.get(message_key, 0) + 1
        self._retries[message_key] = attempt

        if attempt > self.config.max_retries:
            await self._move_to_dead_letter(msg, error)
            return

        logger.exception(
            "Error processing Kafka event at %s:%s:%s; retry %s/%s",
            msg.topic,
            msg.partition,
            msg.offset,
            attempt,
            self.config.max_retries,
        )
        self._schedule_retry(TopicPartition(msg.topic, msg.partition), msg.offset)

    def _schedule_retry(self, partition: TopicPartition, offset: int) -> None:
        if partition in self._retry_tasks:
            return
        self._consumer.pause(partition)
        self._retry_tasks[partition] = asyncio.create_task(
            self._resume_partition_after_delay(partition, offset)
        )

    async def _resume_partition_after_delay(
        self, partition: TopicPartition, offset: int
    ) -> None:
        retry_recovery: bool = False
        try:
            await asyncio.sleep(self.config.retry_delay_seconds)
            self._consumer.seek(partition, offset)
            self._consumer.resume(partition)
        except IllegalStateError:
            retry_recovery = self._is_partition_assigned(partition)
            if retry_recovery:
                logger.warning(
                    "Kafka partition %s failed recovery at offset %s; retrying",
                    partition,
                    offset,
                )
            else:
                logger.warning(
                    "Kafka partition %s was revoked before retrying offset %s; "
                    "leaving it uncommitted for redelivery",
                    partition,
                    offset,
                )
        except Exception:
            retry_recovery = self._is_partition_assigned(partition)
            logger.exception(
                "Kafka partition %s failed recovery at offset %s%s",
                partition,
                offset,
                "; retrying" if retry_recovery else "; leaving it uncommitted",
            )
        finally:
            self._retry_tasks.pop(partition, None)

        if retry_recovery:
            self._schedule_retry(partition, offset)

    def _is_partition_assigned(self, partition: TopicPartition) -> bool:
        try:
            return partition in self._consumer.assignment()
        except Exception:
            logger.exception(
                "Unable to determine Kafka assignment for partition %s", partition
            )
            return False

    # TODO: Implement dead letter reprocessor
    async def _move_to_dead_letter(self, msg: ConsumerRecord, error: Exception) -> None:
        headers = list(msg.headers or [])
        headers.append(("x-dead-letter-error", type(error).__name__.encode()))
        headers.append(("x-dead-letter-source-topic", msg.topic.encode()))
        await self._dead_letter_producer.send_and_wait(
            self.config.dead_letter_topic,
            value=msg.value,
            key=msg.key,
            headers=headers,
        )
        await self._commit(msg)
        logger.error(
            "Moved Kafka event at %s:%s:%s to %s after processing failure",
            msg.topic,
            msg.partition,
            msg.offset,
            self.config.dead_letter_topic,
        )

    async def _commit(self, msg: ConsumerRecord) -> None:
        partition = TopicPartition(msg.topic, msg.partition)
        await self._consumer.commit({partition: msg.offset + 1})
        self._retries.pop(KafkaMessageKey(msg.topic, msg.partition, msg.offset), None)

    async def stop(self):
        if self._consume_task is not None:
            self._consume_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._consume_task
        for task in self._retry_tasks.values():
            task.cancel()
        if self._retry_tasks:
            await asyncio.gather(*self._retry_tasks.values(), return_exceptions=True)
        await self._dead_letter_producer.stop()
        await self._consumer.stop()
