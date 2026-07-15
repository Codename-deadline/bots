import logging

from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message
from telegramify_markdown import markdownify

from common.application.translation import TranslationKey
from telegram.src.bot import dp, translator
from telegram.src.exceptions.invalid_message_format_exception import (
    InvalidMessageFormatException,
)

logger = logging.getLogger(__name__)


@dp.error(
    ExceptionTypeFilter(InvalidMessageFormatException), F.update.message.as_("message")
)
async def invalid_message_format_handler(_: ErrorEvent, message: Message):
    await message.reply(
        markdownify(
            translator.translate(TranslationKey.VALIDATION_INVALID_COMMAND_FORMAT)
        )
    )


@dp.error(ExceptionTypeFilter(TelegramBadRequest))
async def telegram_bad_request_handler(event: ErrorEvent):
    logger.error(event.exception)
