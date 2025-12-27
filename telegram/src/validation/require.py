from collections.abc import Awaitable, Callable

from aiogram import Bot
from aiogram.types import Message

from telegram.src.bot import bot


async def require(
    message: Message, *conditions: Callable[[Message, Bot], Awaitable[None]]
):
    for condition in conditions:
        await condition(message, bot)
