from aiogram.types import (
    Message,
    InlineKeyboardButton,
    CallbackQuery,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from common.config.bot_config import config
from common.i18n import format_with_locale
from common.logic.command_parsers import one_language_optional_arg_parser
from common.logic.enums import Language
from common.logic.utils import get_logger_from_filepath
from telegram.src.markup.schemas.HelpCallbackData import HelpCallbackData


class HelpService:
    __logger = get_logger_from_filepath(__file__)
    button_title_keys: tuple = ("start", "subscription", "chat", "verification")

    @staticmethod
    def __get_language(message_text: str) -> Language:
        return (
            one_language_optional_arg_parser(message_text) or config.fallback_language
        )

    def __build_markup(
        self, language: Language, current_page: str
    ) -> InlineKeyboardMarkup:
        return (
            InlineKeyboardBuilder()
            .row(
                *[
                    InlineKeyboardButton(
                        text=format_with_locale(f"help.{key}.title", language),
                        callback_data=HelpCallbackData(
                            page=key, language=language
                        ).pack(),
                    )
                    for key in self.button_title_keys
                    if key != current_page
                ],
                width=2,
            )
            .as_markup()
        )

    async def display_base_help(self, message: Message):
        language: Language = self.__get_language(message.text)
        await message.reply(
            text=format_with_locale("help.start.text", language),
            reply_markup=self.__build_markup(language, "start"),
        )

    async def handle_page_change(self, call: CallbackQuery, data: HelpCallbackData):
        title: str = format_with_locale(f"help.{data.page}.title", data.language)
        current_page_text: str = "" + format_with_locale(
            f"help.current_page", data.language, title=title
        )
        main_text: str = format_with_locale(f"help.{data.page}.text", data.language)
        await call.message.edit_text(
            f"{current_page_text}\n{main_text}",
            reply_markup=self.__build_markup(data.language, data.page),
        )
