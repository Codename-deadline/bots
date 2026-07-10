from aiogram import Router
from aiogram.types import CallbackQuery

from common.application.services.verification_service import VerificationService
from telegram.src.mapping.callbacks import to_option_selection
from telegram.src.markup.schemas.AccountLinkageCallbackData import (
    AccountLinkageCallbackData,
)

verification_router: Router = Router()


@verification_router.callback_query(AccountLinkageCallbackData.filter())
async def handle_account_linkage_response(
    call: CallbackQuery,
    callback_data: AccountLinkageCallbackData,
    verification_service: VerificationService,
):
    await verification_service.handle_selection(
        to_option_selection(call, callback_data)
    )
    await call.answer()
