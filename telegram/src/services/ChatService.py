from aiogram.types import Message

from common.i18n import format_with_locale
from common.logic.command_parsers import (
    one_language_arg_parser,
    one_language_optional_arg_parser,
    parse_command,
)
from common.logic.enums import Language
from common.logic.grpc.GrpcClient import GrpcClient
from common.logic.utils import get_logger_from_filepath
from telegram.src.validation import require
from telegram.src.validation.conditions import has_admin_rights, not_dm


class ChatService:
    __logger = get_logger_from_filepath(__file__)

    def __init__(self, grpc_client):
        self.grpc_client: GrpcClient = grpc_client

    async def register_chat(self, message: Message):
        await require(message, not_dm, has_admin_rights)

        language: Language = parse_command(message.text, one_language_arg_parser)
        res = await self.grpc_client.register_chat(
            message.from_user.id, message.chat.id, message.chat.title, language
        )
        await message.reply(format_with_locale(res))

    async def deregister_chat(self, message: Message):
        await require(message, not_dm, has_admin_rights)

        res = await self.grpc_client.deregister_chat(message.chat.id)
        await message.reply(format_with_locale(res))

    async def update_chat_info(self, message: Message):
        language: Language | None = one_language_optional_arg_parser(message.text)
        await require(message, not_dm, has_admin_rights)

        res = await self.grpc_client.update_chat_info(
            message.from_user.id, message.chat.id, message.chat.title, language
        )
        await message.reply(format_with_locale(res))
