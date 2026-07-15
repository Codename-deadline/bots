from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from telegramify_markdown import markdownify

from common.application.protocols.translator import Translator
from common.application.translation import TranslationKey

util_router = Router()


@util_router.message(Command("my_id"))
async def send_user_id(message: Message, translator: Translator):
    if message.from_user is None:
        return

    await message.reply(
        markdownify(
            translator.translate(
                TranslationKey.USER_ID_SUCCESS, user_id=message.from_user.id
            )
        )
    )
