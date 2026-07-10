from typing import cast

from aiogram.types import CallbackQuery
from aiogram.types import Message as TelegramMessage

from common.contracts.choice.option_selection import OptionSelection
from common.contracts.interaction import VerificationInteraction
from telegram.src.markup.schemas.choice_callback_data import ChoiceCallbackData


def to_option_selection(
    call: CallbackQuery, data: ChoiceCallbackData
) -> OptionSelection:
    # Choice callbacks are generated only for buttons attached to bot messages.
    message = cast(TelegramMessage, call.message)
    return OptionSelection(
        prompt_id=data.prompt_id,
        account_id=call.from_user.id,
        chat_id=message.chat.id,
        message_id=message.message_id,
        interaction=VerificationInteraction(data.interaction),
        value=data.value,
    )
