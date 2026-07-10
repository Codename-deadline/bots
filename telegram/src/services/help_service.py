from enum import StrEnum

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telegramify_markdown import markdownify

from common.application.arg_parsers import parse_optional_language
from common.application.enums import Language
from common.application.protocols.translator import Translator
from common.application.translation import TranslationKey
from common.config.bot_config import config
from telegram.src.markup.schemas.HelpCallbackData import HelpCallbackData


class HelpPage(StrEnum):
    START = "start"
    SUBSCRIPTION = "subscription"
    CHAT = "chat"
    VERIFICATION = "verification"

    @property
    def title_key(self) -> TranslationKey:
        return {
            HelpPage.START: TranslationKey.HELP_START_TITLE,
            HelpPage.SUBSCRIPTION: TranslationKey.HELP_SUBSCRIPTION_TITLE,
            HelpPage.CHAT: TranslationKey.HELP_CHAT_TITLE,
            HelpPage.VERIFICATION: TranslationKey.HELP_VERIFICATION_TITLE,
        }[self]

    @property
    def text_key(self) -> TranslationKey:
        return {
            HelpPage.START: TranslationKey.HELP_START_TEXT,
            HelpPage.SUBSCRIPTION: TranslationKey.HELP_SUBSCRIPTION_TEXT,
            HelpPage.CHAT: TranslationKey.HELP_CHAT_TEXT,
            HelpPage.VERIFICATION: TranslationKey.HELP_VERIFICATION_TEXT,
        }[self]


class HelpService:
    pages: tuple[HelpPage, ...] = tuple(HelpPage)

    def __init__(self, translator: Translator):
        self.translator = translator

    @staticmethod
    def __get_language(args: tuple[str, ...]) -> Language:
        parsed_language = parse_optional_language(args)
        if parsed_language.error is not None:
            return config.fallback_language
        return parsed_language.as_optional_value() or config.fallback_language

    def __build_markup(
        self, language: Language, current_page: HelpPage
    ) -> InlineKeyboardMarkup:
        return (  # pyright: ignore[reportReturnType]. This is valid. See .as_markup() impl
            InlineKeyboardBuilder()
            .row(
                *[
                    InlineKeyboardButton(
                        text=self.translator.translate(page.title_key, language),
                        callback_data=HelpCallbackData(
                            page=page.value, language=language
                        ).pack(),
                    )
                    for page in self.pages
                    if page != current_page
                ],
                width=2,
            )
            .as_markup()
        )

    async def display_base_help(self, message: Message, args: tuple[str, ...]):
        language = self.__get_language(args)
        await message.reply(
            text=markdownify(
                self.translator.translate(TranslationKey.HELP_START_TEXT, language)
            ),
            reply_markup=self.__build_markup(language, HelpPage.START),
        )

    async def handle_page_change(self, call: CallbackQuery, data: HelpCallbackData):
        page = HelpPage(data.page)
        title = self.translator.translate(page.title_key, data.language)
        current_page_text = self.translator.translate(
            TranslationKey.HELP_CURRENT_PAGE, data.language, title=title
        )
        main_text = self.translator.translate(page.text_key, data.language)

        await call.message.edit_text(
            markdownify(f"{current_page_text}\n{main_text}"),
            reply_markup=self.__build_markup(data.language, page),
        )
