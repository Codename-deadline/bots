from collections.abc import Callable

from common.application.protocols.messenger_adapter import MessengerAdapter
from common.application.protocols.translator import Translator
from common.contracts.choice.choice_prompt import ChoicePrompt


class ConsoleMessengerAdapter(MessengerAdapter):
    def __init__(self, translator: Translator):
        self.translator = translator

    async def send_message(self, chat_id: int, text: str) -> None:
        print(f"[chat:{chat_id}] {text}")

    async def reply_to_message(self, chat_id: int, message_id: int, text: str) -> None:
        print(f"[chat:{chat_id} reply_to:{message_id}] {text}")

    async def edit_message(
        self, chat_id: int, message_id: int, update: Callable[[str], str]
    ) -> None:
        print(f"[chat:{chat_id} edit:{message_id}] {update('')}")

    async def send_choice_prompt(
        self, chat_id: int, options: ChoicePrompt, options_per_line: int = 2
    ) -> None:
        text = self.translator.translate(options.text_key)
        choices = ", ".join(
            f"{choice.value}={self.translator.translate(choice.label_key)}"
            for choice in options.choices
        )
        print(
            f"[chat:{chat_id} prompt:{options.interaction}] {text}\nChoices: {choices}"
        )
