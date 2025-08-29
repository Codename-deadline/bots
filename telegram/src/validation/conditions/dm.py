from aiogram import Bot
from aiogram.types import Message

from telegram.src.exceptions.InvalidChatException import InvalidChatException


async def not_dm(message: Message, bot: Bot):
    if message.chat.type == "private":
        raise InvalidChatException(is_dm=True)
