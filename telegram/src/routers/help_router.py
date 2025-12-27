from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from telegram.src.markup.schemas.HelpCallbackData import HelpCallbackData
from telegram.src.services.help_service import HelpService

help_router: Router = Router()


@help_router.message(Command("help"))
async def base_help(message: Message, help_service: HelpService):
    await help_service.display_base_help(message)


@help_router.callback_query(HelpCallbackData.filter())
async def handle_account_linkage_response(
    call: CallbackQuery,
    callback_data: HelpCallbackData,
    help_service: HelpService,
):
    await help_service.handle_page_change(call, callback_data)
