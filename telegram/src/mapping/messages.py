from aiogram import Bot
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner, Message

from common.application.enums import Language
from common.contracts.incoming_message import IncomingMessage


def _resolve_language(message: Message) -> Language | None:
    language_code = message.from_user.language_code if message.from_user else None
    if language_code is None:
        return None
    try:
        return Language(language_code.upper())
    except ValueError:
        return None


async def to_incoming_message(
    message: Message, bot: Bot, resolve_admin: bool = False
) -> IncomingMessage:
    is_private = message.chat.type == "private"
    has_chat_admin_rights = False
    if resolve_admin and not is_private and message.from_user is not None:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        has_chat_admin_rights = isinstance(
            member, (ChatMemberAdministrator, ChatMemberOwner)
        )

    return IncomingMessage(
        id=message.message_id,
        account_id=message.from_user.id if message.from_user else 0,
        chat_id=message.chat.id,
        chat_title=message.chat.title or "",
        text=message.text or "",
        language=_resolve_language(message),
        is_private=is_private,
        has_chat_admin_rights=has_chat_admin_rights,
    )
