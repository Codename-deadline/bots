from common.application.protocols.messenger_adapter import MessengerAdapter
from common.application.protocols.translator import Translator
from common.application.services.verification_service import VerificationService
from common.application.translation import TranslationKey
from common.config.schemas.kafka_config import KafkaConfig
from common.contracts.app_redirect import AppRedirect
from common.contracts.interaction import VerificationInteraction
from common.infrastructure.kafka.integration_events import (
    IntegrationEventHandlers,
    build_integration_consumer,
)
from common.infrastructure.kafka.notification_renderer import render_notification
from common.infrastructure.kafka.schemas.account_linkage_event import (
    AccountLinkageEvent,
)
from common.infrastructure.kafka.schemas.notification_event import NotificationEvent
from common.infrastructure.kafka.schemas.otp_event import OtpEvent


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
        await messenger.send_message(
            event.chat_id,
            render_notification(event, translator),
            AppRedirect(
                path=f"/deadline?ddlId={event.deadline.id}",
                display_text=translator.translate(
                    TranslationKey.NOTIFICATIONS_GO_TO_DEADLINE, event.language
                ),
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
