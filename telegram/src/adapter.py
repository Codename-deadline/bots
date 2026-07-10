from collections.abc import Callable

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, ReplyParameters
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telegramify_markdown import markdownify

from common.application.protocols.messenger_adapter import MessengerAdapter
from common.application.protocols.translator import Translator
from common.contracts.choice.choice_prompt import ChoicePrompt
from telegram.src.markup.schemas.choice_callback_data import ChoiceCallbackData


class TelegramMessengerAdapter(MessengerAdapter):
    def __init__(self, bot: Bot, translator: Translator):
        self.bot = bot
        self.translator = translator

    def _render(self, text: str) -> str:
        return markdownify(text)

    async def send_message(self, chat_id: int, text: str) -> None:
        await self.send_message(chat_id, self._render(text))

    async def reply_to_message(self, chat_id: int, message_id: int, text: str) -> None:
        await self.bot.send_message(
            chat_id,
            self._render(text),
            reply_parameters=ReplyParameters(message_id=message_id),
        )

    async def edit_message(
        self, chat_id: int, message_id: int, update: Callable[[str], str]
    ) -> None:
        await self.bot.edit_message_text(
            self._render(update("")),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None,
        )

    async def send_choice_prompt(
        self, chat_id: int, options: ChoicePrompt, options_per_line: int = 2
    ) -> None:
        builder = InlineKeyboardBuilder()
        builder.row(
            *[
                InlineKeyboardButton(
                    text=self.translator.translate(choice.label_key),
                    callback_data=ChoiceCallbackData(
                        prompt_id=options.id,
                        interaction=options.interaction.value,
                        value=choice.value,
                    ).pack(),
                )
                for choice in options.choices
            ],
            width=options_per_line,
        )
        await self.bot.send_message(
            chat_id,
            self._render(self.translator.translate(options.text_key)),
            reply_markup=builder.as_markup(),
        )
