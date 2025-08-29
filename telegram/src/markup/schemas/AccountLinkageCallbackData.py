from aiogram.filters.callback_data import CallbackData


class AccountLinkageCallbackData(CallbackData, prefix="ald"):
    request_id: str
    is_accepted: bool
