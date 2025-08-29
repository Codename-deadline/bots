from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from common.config.bot_config import config
from common.logic.enums import Messenger
from common.logic.grpc.GrpcClient import GrpcClient

dp: Dispatcher = Dispatcher()
bot: Bot = Bot(
    token=config.token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
)
telegram_grpc_client: GrpcClient = GrpcClient(
    config.grpc.target,
    Messenger.TELEGRAM,
    config.id,
    config.grpc.is_secure,
    config.grpc.credentials,
)
