from aiogram.filters.callback_data import CallbackData


class AccountLinkageCallbackData(CallbackData, prefix="ald"):
    prompt_id: str
    interaction: str
    value: str
