from dataclasses import dataclass

from common.logic.enums import Language


@dataclass
class IncomingMessage:
    id: int
    account_id: int
    chat_id: int
    chat_title: str
    text: str
    language: Language | None
    is_private: bool
    has_chat_admin_rights: bool
