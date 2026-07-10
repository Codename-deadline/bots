from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from common.application.enums import Messenger
from common.application.gateways.grpc_integration_gateway import GrpcIntegrationGateway
from common.application.services.chat_service import ChatService
from common.application.services.subscription_service import SubscriptionService
from common.application.services.verification_service import VerificationService
from common.config.bot_config import config
from common.infrastructure.i18n.translator import I18nTranslator
from telegram.src.adapter import TelegramMessengerAdapter
from telegram.src.kafka_consumer import build_telegram_consumer
from telegram.src.services.help_service import HelpService

dp: Dispatcher = Dispatcher()
bot: Bot = Bot(
    token=config.token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
)
integration_gateway = GrpcIntegrationGateway(
    config.grpc.target,
    Messenger.TELEGRAM,
    config.id,
    config.grpc.is_secure,
    config.grpc.credentials,
)
translator = I18nTranslator(config.fallback_language)
telegram_adapter = TelegramMessengerAdapter(bot, translator)

chat_service = ChatService(telegram_adapter, integration_gateway, translator)
subscription_service = SubscriptionService(
    telegram_adapter, integration_gateway, translator
)
verification_service = VerificationService(
    telegram_adapter, integration_gateway, translator
)
help_service = HelpService(translator)

global_consumer = build_telegram_consumer(
    config.kafka,
    verification_service,
    telegram_adapter,
    translator,
)
