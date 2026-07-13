from collections.abc import Callable
from datetime import UTC, datetime

from common.application.enums import Language
from common.application.protocols.integration_gateway import IntegrationResponse
from common.application.services.verification_service import VerificationService
from common.application.translation import TranslationKey
from common.config.schemas.kafka_config import KafkaConfig
from common.config.schemas.kafka_topics_config import KafkaTopicsConfig
from common.config.schemas.tls_config import TlsConfig
from common.contracts.choice.choice_prompt import ChoicePrompt
from common.infrastructure.kafka.enums.time_remaining import TimeRemaining
from common.infrastructure.kafka.schemas.notification_event import (
    DeadlinePayload,
    NotificationEvent,
    RawEntityPayload,
)
from telegram.src.kafka_consumer import build_telegram_consumer
from tests.common.application.services.fakes import (
    FakeIntegrationGateway,
    FakeMessenger,
    FakeTranslator,
)


class RecordingMessenger:
    def __init__(self):
        self.messages = []

    async def send_message(self, chat_id: int, text: str) -> None:
        self.messages.append((chat_id, text))

    async def reply_to_message(self, chat_id: int, message_id: int, text: str) -> None:
        return None

    async def edit_message(
        self, chat_id: int, message_id: int, update: Callable[[str], str]
    ) -> None:
        return None

    async def send_choice_prompt(
        self, chat_id: int, options: ChoicePrompt, options_per_line: int = 2
    ) -> None:
        return None


class RecordingTranslator:
    def __init__(self):
        self.calls = []

    def translate(
        self,
        key: TranslationKey,
        language: Language | None = None,
        **params,
    ) -> str:
        self.calls.append((key, language, params))
        return "translated"

    def translate_response(self, response: IntegrationResponse, **params) -> str:
        return "translated"


async def test_notification_includes_organization_and_thread_in_translation():
    config = KafkaConfig(
        bootstrap_servers="localhost:9092",
        consumer_group="deadlines-test",
        dead_letter_topic="dead-letter",
        max_retries=5,
        retry_delay_seconds=5.0,
        topics=KafkaTopicsConfig(
            account_linkage="account-linkage",
            notifications="notifications",
            otp="otp",
        ),
        tls=TlsConfig(
            enabled=False,
            ca_certificate=None,
            certificate=None,
            private_key=None,
        ),
    )
    messenger = RecordingMessenger()
    translator = RecordingTranslator()
    consumer = build_telegram_consumer(
        config,
        VerificationService(
            FakeMessenger(), FakeIntegrationGateway(), FakeTranslator()
        ),
        messenger,
        translator,
    )
    event = NotificationEvent.model_validate(
        {
            "chatId": 1,
            "language": Language.EN,
            "organization": RawEntityPayload(id=2, title="Organization"),
            "thread": RawEntityPayload(id=3, title="Thread"),
            "deadline": DeadlinePayload(
                id=4,
                title="Deadline",
                due=datetime(2026, 1, 1, tzinfo=UTC),
            ),
            "timeRemaining": TimeRemaining.ONE_DAY,
        }
    )

    await consumer._event_handlers[config.topics.notifications].handler(event)

    _, _, params = translator.calls[-1]
    assert params["organization"] == "Organization"
    assert params["thread"] == "Thread"
    assert messenger.messages == [(1, "translated")]
