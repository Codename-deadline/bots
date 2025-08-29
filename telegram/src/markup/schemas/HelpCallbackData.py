from aiogram.filters.callback_data import CallbackData

from common.logic.enums import Language


class HelpCallbackData(CallbackData, prefix="hcd"):
    page: str
    language: Language
