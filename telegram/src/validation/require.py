from collections.abc import Callable, Awaitable

from telegram.src.bot import bot
from aiogram import Bot
from aiogram.types import Message


async def require(
    message: Message, *conditions: Callable[[Message, Bot], Awaitable[None]]
):
    for condition in conditions:
        await condition(message, bot)
