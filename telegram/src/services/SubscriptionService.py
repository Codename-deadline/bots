from aiogram.types import Message

from common.i18n import format_with_locale
from common.logic.command_parsers import (
    parse_command,
    one_int_arg_parser,
)
from common.logic.grpc.GrpcClient import GrpcClient
from common.logic.utils import get_logger_from_filepath


class SubscriptionService:
    __logger = get_logger_from_filepath(__file__)

    def __init__(self, grpc_client):
        self.grpc_client: GrpcClient = grpc_client

    async def __subscribe_to(self, message: Message, grpc_callback):
        target_id: int = parse_command(message.text, one_int_arg_parser)
        res = await grpc_callback(message.from_user.id, target_id, message.chat.id)
        if res.is_error:
            self.__logger.error("[Sub]: %s", res.key)

        await message.reply(format_with_locale(res))

    async def subscribe_to_organization(self, message: Message):
        await self.__subscribe_to(message, self.grpc_client.subscribe_to_organization)

    async def subscribe_to_thread(self, message: Message):
        await self.__subscribe_to(message, self.grpc_client.subscribe_to_thread)

    async def subscribe_to_deadline(self, message: Message):
        await self.__subscribe_to(message, self.grpc_client.subscribe_to_deadline)

    async def __unsubscribe_from(self, message: Message, grpc_callback):
        target_id: int = parse_command(message.text, one_int_arg_parser)
        res = await grpc_callback(message.from_user.id, target_id, message.chat.id)
        if res.is_error:
            self.__logger.error("[Unsub]: %s", res.key)

        await message.reply(format_with_locale(res))

    async def unsubscribe_from_organization(self, message: Message):
        await self.__unsubscribe_from(
            message, self.grpc_client.unsubscribe_from_organization
        )

    async def unsubscribe_from_thread(self, message: Message):
        await self.__unsubscribe_from(message, self.grpc_client.unsubscribe_from_thread)

    async def unsubscribe_from_deadline(self, message: Message):
        await self.__unsubscribe_from(
            message, self.grpc_client.unsubscribe_from_deadline
        )

    async def unsubscribe_from_all(self, message: Message):
        res = await self.grpc_client.unsubscribe_from_all(
            message.from_user.id, message.chat.id
        )
        if res.is_error:
            self.__logger.error("[Unsub]: %s", res.key)

        await message.reply(format_with_locale(res))
