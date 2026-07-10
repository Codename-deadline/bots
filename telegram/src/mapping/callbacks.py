from aiogram.types import CallbackQuery

from common.contracts.choice.option_selection import OptionSelection
from common.contracts.interaction import VerificationInteraction
from telegram.src.markup.schemas.AccountLinkageCallbackData import (
    AccountLinkageCallbackData,
)


def to_option_selection(
    call: CallbackQuery, data: AccountLinkageCallbackData
) -> OptionSelection:
    return OptionSelection(
        prompt_id=data.prompt_id,
        account_id=call.from_user.id,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        interaction=VerificationInteraction(data.interaction),
        value=data.value,
    )
