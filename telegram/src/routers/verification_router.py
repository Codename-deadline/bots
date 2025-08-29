from aiogram import Router
from aiogram.types import CallbackQuery

from telegram.src.markup.schemas.AccountLinkageCallbackData import (
    AccountLinkageCallbackData,
)
from telegram.src.services.VerificationService import VerificationService

verification_router: Router = Router()


@verification_router.callback_query(AccountLinkageCallbackData.filter())
async def handle_account_linkage_response(
    call: CallbackQuery,
    callback_data: AccountLinkageCallbackData,
    verification_service: VerificationService,
):
    await verification_service.handle_account_linkage_response(call, callback_data)
