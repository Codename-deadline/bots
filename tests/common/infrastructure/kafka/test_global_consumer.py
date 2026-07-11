import asyncio
from contextlib import suppress
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, Mock

from aiokafka.errors import IllegalStateError
from aiokafka.structs import ConsumerRecord, TopicPartition

from common.config.schemas.kafka_config import KafkaConfig
from common.infrastructure.kafka.consumers.global_consumer import (
    GlobalConsumer,
    KafkaMessageKey,
)


def _consumer() -> GlobalConsumer:
    return GlobalConsumer(
        KafkaConfig(
            bootstrap_servers="localhost:9092",
            retry_delay_seconds=0.001,
        )
    )


async def test_retry_pauses_only_failed_partition_then_rewinds_and_resumes():
    consumer = _consumer()
    consumer._consumer = Mock()
    partition = TopicPartition("notifications", 2)

    consumer._schedule_retry(partition, 7)

    consumer._consumer.pause.assert_called_once_with(partition)
    consumer._consumer.seek.assert_not_called()
    await consumer._retry_tasks[partition]

    consumer._consumer.seek.assert_called_once_with(partition, 7)
    consumer._consumer.resume.assert_called_once_with(partition)
    assert consumer._retry_tasks == {}


async def test_revoked_partition_during_seek_does_not_crash_retry_task():
    consumer = _consumer()
    consumer._consumer = Mock()
    consumer._consumer.seek.side_effect = IllegalStateError("partition revoked")
    consumer._consumer.assignment.return_value = set()
    partition = TopicPartition("notifications", 2)

    consumer._schedule_retry(partition, 7)

    await consumer._retry_tasks[partition]

    consumer._consumer.resume.assert_not_called()
    assert consumer._retry_tasks == {}


async def test_assigned_partition_reschedules_when_resume_fails():
    consumer = _consumer()
    consumer._consumer = Mock()
    consumer._consumer.resume.side_effect = IllegalStateError("temporary failure")
    partition = TopicPartition("notifications", 2)
    consumer._consumer.assignment.return_value = {partition}

    consumer._schedule_retry(partition, 7)
    first_retry = consumer._retry_tasks[partition]
    await first_retry

    assert consumer._consumer.pause.call_count == 2
    retry_task = consumer._retry_tasks[partition]
    retry_task.cancel()
    with suppress(asyncio.CancelledError):
        await retry_task


async def test_commit_only_advances_processed_partition_offset():
    consumer = _consumer()
    consumer._consumer = Mock()
    consumer._consumer.commit = AsyncMock()
    message = cast(
        ConsumerRecord[object, object],
        SimpleNamespace(topic="notifications", partition=2, offset=7),
    )
    consumer._retries[KafkaMessageKey("notifications", 2, 7)] = 1

    await consumer._commit(message)

    consumer._consumer.commit.assert_awaited_once_with(
        {TopicPartition("notifications", 2): 8}
    )
    assert consumer._retries == {}
