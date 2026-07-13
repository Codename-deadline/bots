import asyncio
from contextlib import suppress
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, Mock, patch

from aiokafka.errors import IllegalStateError
from aiokafka.structs import ConsumerRecord, TopicPartition

from common.config.schemas.kafka_config import KafkaConfig
from common.config.schemas.tls_config import TlsConfig
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


def test_connection_options_uses_plaintext_when_tls_is_disabled():
    options = _consumer()._connection_options()

    assert options.security_protocol == "PLAINTEXT"
    assert options.ssl_context is None


def test_connection_options_creates_mutual_tls_context(tmp_path):
    ca_certificate = tmp_path / "ca.crt"
    certificate = tmp_path / "client.crt"
    private_key = tmp_path / "client.key"
    for path in (ca_certificate, certificate, private_key):
        path.write_text(path.name)
    consumer = GlobalConsumer(
        KafkaConfig(
            bootstrap_servers="localhost:9092",
            tls=TlsConfig(
                enabled=True,
                ca_certificate=ca_certificate,
                certificate=certificate,
                private_key=private_key,
            ),
        )
    )
    ssl_context = Mock()

    with patch(
        "common.infrastructure.kafka.consumers.global_consumer.ssl.create_default_context",
        return_value=ssl_context,
    ) as create_default_context:
        options = consumer._connection_options()

    create_default_context.assert_called_once_with(cafile=ca_certificate)
    ssl_context.load_cert_chain.assert_called_once_with(certificate, private_key)
    assert options.security_protocol == "SSL"
    assert options.ssl_context is ssl_context


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
