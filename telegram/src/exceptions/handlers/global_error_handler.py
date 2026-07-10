import logging

from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message
from telegramify_markdown import markdownify

from common.application.translation import TranslationKey
from telegram.src.bot import dp, translator
from telegram.src.exceptions import InvalidChatException, InvalidMessageFormatException
from telegram.src.exceptions.AccessDeniedException import AccessDeniedException

logger = logging.getLogger(__name__)


@dp.error(
    ExceptionTypeFilter(InvalidMessageFormatException), F.update.message.as_("message")
)
async def invalid_message_format_handler(event: ErrorEvent, message: Message):
    await message.reply(
        markdownify(translator.translate(TranslationKey.VALIDATION_INVALID_COMMAND_FORMAT))
    )


@dp.error(ExceptionTypeFilter(TelegramBadRequest))
async def telegram_bad_request_handler(event: ErrorEvent):
    logger.error(event.exception)


@dp.error(ExceptionTypeFilter(InvalidChatException), F.update.message.as_("message"))
async def invalid_chat_type_exception_handler(event: ErrorEvent, message: Message):
    await message.reply(
        markdownify(
            translator.translate(
                TranslationKey.VALIDATION_DM_NOT_ALLOWED
                if event.exception.is_dm
                else TranslationKey.VALIDATION_CHAT_NOT_ALLOWED
            )
        )
    )


@dp.error(ExceptionTypeFilter(AccessDeniedException), F.update.message.as_("message"))
async def access_denied_exception_handler(event: ErrorEvent, message: Message):
    await message.reply(
        markdownify(translator.translate(TranslationKey.VALIDATION_ADMINS_ONLY_CMD))
    )
