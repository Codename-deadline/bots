from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from common.i18n import format_with_locale

util_router = Router()


@util_router.message(Command("my_id"))
async def send_user_id(message: Message):
    await message.reply(
        format_with_locale("user_id.success", user_id=message.from_user.id)
    )
