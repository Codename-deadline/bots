from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from common.application.translation import TranslationKey
from telegram.src.services.util_service import UtilService

util_router = Router()


@util_router.message(Command("my_id"))
async def send_user_id(message: Message, util_service: UtilService):
    await util_service.respond_with_user_id(message, TranslationKey.USER_ID_SUCCESS)


@util_router.message(Command("start"))
async def respond_to_start(message: Message, util_service: UtilService):
    await util_service.respond_with_user_id(message, TranslationKey.START_RESPONSE)
