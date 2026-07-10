from common.application.protocols.messenger_adapter import MessengerAdapter
from common.application.protocols.translator import Translator
from common.application.services.verification_service import VerificationService
from common.application.translation import TranslationKey
from common.config.schemas.KafkaConfig import KafkaConfig
from common.contracts.interaction import VerificationInteraction
from common.infrastructure.i18n.mappings import TIME_REMAINING_TRANSLATION_KEYS
from common.infrastructure.kafka.integration_events import (
    IntegrationEventHandlers,
    build_integration_consumer,
)
from common.infrastructure.kafka.schemas.AccountLinkageEvent import AccountLinkageEvent
from common.infrastructure.kafka.schemas.NotificationEvent import NotificationEvent
from common.infrastructure.kafka.schemas.OtpEvent import OtpEvent


def build_telegram_consumer(
    kafka_config: KafkaConfig,
    verification_service: VerificationService,
    messenger: MessengerAdapter,
    translator: Translator,
):
    async def handle_account_linkage(event: AccountLinkageEvent) -> None:
        await verification_service.ask_for_confirmation(
            event.account_id,
            event.request_id,
            VerificationInteraction.ACCOUNT_LINKING,
        )

    async def handle_notification(event: NotificationEvent) -> None:
        time_remaining = translator.translate(
            TIME_REMAINING_TRANSLATION_KEYS[event.timeRemaining], event.language
        )
        await messenger.send_message(
            event.chat_id,
            translator.translate(
                TranslationKey.NOTIFICATIONS_DEADLINE_EXPIRY,
                event.language,
                title=event.deadline.title,
                due=f"{event.deadline.due.strftime('%H:%M %d.%m.%Y')} UTC+0",
                time_remaining=time_remaining,
            ),
        )

    async def handle_otp(event: OtpEvent) -> None:
        await messenger.send_message(
            event.account_id,
            translator.translate(
                TranslationKey.AUTH_OTP_TEXT, event.language, code=event.code
            ),
        )

    return build_integration_consumer(
        kafka_config,
        IntegrationEventHandlers(
            account_linkage=handle_account_linkage,
            notifications=handle_notification,
            otp=handle_otp,
        ),
    )
