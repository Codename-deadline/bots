from collections.abc import Callable
from typing import Protocol

from common.contracts.choice.choice_prompt import ChoicePrompt
from common.contracts.incoming_message import IncomingMessage


class MessengerAdapter(Protocol):
    async def send_message(self, chat_id: int, text: str) -> None: ...

    async def reply_to_message(
        self, chat_id: int, message_id: int, text: str
    ) -> None: ...
    async def edit_message(
        self, chat_id: int, message_id: int, update: Callable[[str], str]
    ) -> None: ...

    async def send_choice_prompt(self, chat_id: int, options: ChoicePrompt) -> None: ...
