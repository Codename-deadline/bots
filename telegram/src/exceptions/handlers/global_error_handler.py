from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram import F
from aiogram.types import ErrorEvent, Message

from common.i18n import format_with_locale
from common.logic.utils import get_logger_from_filepath
from telegram.src.bot import dp
from telegram.src.exceptions import InvalidChatException, InvalidMessageFormatException

from telegram.src.exceptions.AccessDeniedException import AccessDeniedException

logger = get_logger_from_filepath(__file__)


@dp.error(ExceptionTypeFilter(InvalidMessageFormatException), F.update.message.as_("message"))
async def invalid_message_format_handler(event: ErrorEvent, message: Message):
    await message.reply(format_with_locale("validation.invalid_cmd_format"))


@dp.error(ExceptionTypeFilter(TelegramBadRequest))
async def telegram_bad_request_handler(event: ErrorEvent):
    logger.error(event.exception)


@dp.error(ExceptionTypeFilter(InvalidChatException), F.update.message.as_("message"))
async def invalid_chat_type_exception_handler(event: ErrorEvent, message: Message):
    await message.reply(
        format_with_locale(
            "validation.dm_not_allowed"
            if event.exception.is_dm
            else "validation.chat_not_allowed"
        )
    )


@dp.error(ExceptionTypeFilter(AccessDeniedException), F.update.message.as_("message"))
async def access_denied_exception_handler(event: ErrorEvent, message: Message):
    await message.reply(format_with_locale("validation.admins_only_cmd"))
