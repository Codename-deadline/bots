from aiogram.types import Message
from telegramify_markdown import markdownify

from common.application.protocols.translator import Translator
from common.application.translation import TranslationKey


class UtilService:
    def __init__(self, translator: Translator):
        self.translator = translator

    async def respond_with_user_id(
        self, message: Message, translation_key: TranslationKey
    ):
        if message.from_user is None:
            return

        await message.reply(
            markdownify(
                self.translator.translate(translation_key, user_id=message.from_user.id)
            )
        )
