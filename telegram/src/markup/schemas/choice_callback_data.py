from aiogram.filters.callback_data import CallbackData


class ChoiceCallbackData(CallbackData, prefix="choice"):
    prompt_id: str
    interaction: str
    value: str
