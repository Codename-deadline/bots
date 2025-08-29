from aiogram import Bot
from aiogram.types import Message, ChatMemberAdministrator, ChatMemberOwner

from telegram.src.exceptions.AccessDeniedException import AccessDeniedException


async def has_admin_rights(message: Message, bot: Bot):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if not isinstance(member, (ChatMemberAdministrator, ChatMemberOwner)):
        raise AccessDeniedException
