from common.config.bot_config import config
from common.kafka.schemas.AccountLinkageEvent import AccountLinkageEvent
from common.kafka.schemas.NotificationEvent import NotificationEvent
from common.kafka import GlobalConsumer, EventHandler
from common.kafka.schemas.OtpEvent import OtpEvent
from telegram.src.bot import telegram_grpc_client
from telegram.src.services.MessageService import MessageService


global_consumer: GlobalConsumer = GlobalConsumer(config.kafka, telegram_grpc_client)


def kafka_handlers_setup():
    global_consumer.register_handler(
        EventHandler(
            "private.integration.accountlinkage",
            AccountLinkageEvent,
            MessageService.link_account_send_message,
        )
    )
    global_consumer.register_handler(
        EventHandler(
            "private.integration.notifications",
            NotificationEvent,
            MessageService.deadline_notification_send_message,
        )
    )
    global_consumer.register_handler(
        EventHandler(
            "private.auth.otp",
            OtpEvent,
            MessageService.otp_code_send_message
        )
    )
