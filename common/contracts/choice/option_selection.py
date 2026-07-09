from dataclasses import dataclass


@dataclass
class OptionSelection:
    request_id: str
    account_id: int
    chat_id: int
    message_id: int
    interaction: str
    value: str
