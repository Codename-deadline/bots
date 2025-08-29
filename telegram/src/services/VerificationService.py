from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from common.i18n import format_with_locale
from common.logic.grpc.GrpcClient import GrpcClient
from common.logic.utils import get_logger_from_filepath
from telegram.src.markup.schemas.AccountLinkageCallbackData import (
    AccountLinkageCallbackData,
)


class VerificationService:
    __logger = get_logger_from_filepath(__file__)

    def __init__(self, grpc_client):
        self.grpc_client: GrpcClient = grpc_client

    async def handle_account_linkage_response(
        self, call: CallbackQuery, data: AccountLinkageCallbackData
    ):
        await call.message.edit_reply_markup(reply_markup=None)
        res = await self.grpc_client.link_messenger_account(
            data.request_id, data.is_accepted
        )
        if res.is_error:
            self.__logger.error("[Account linkage]: %s", res.key)

        await call.message.edit_text(
            f"<s>{call.message.text}</s>\n{format_with_locale(res.key)}",
            parse_mode=ParseMode.HTML,
        )
