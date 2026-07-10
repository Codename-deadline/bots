import logging
from collections.abc import Awaitable, Callable
from typing import Final

from common.application.protocols.integration_gateway import IntegrationGateway
from common.application.protocols.messenger_adapter import MessengerAdapter
from common.application.protocols.translator import Translator
from common.application.translation import TranslationKey
from common.contracts.choice.choice import Choice
from common.contracts.choice.choice_prompt import ChoicePrompt
from common.contracts.choice.option_selection import OptionSelection
from common.contracts.interaction import VerificationInteraction

logger = logging.getLogger(__name__)


class VerificationService:
    CHOICE_ACCEPT: Final[str] = "accept"
    CHOICE_REJECT: Final[str] = "reject"

    def __init__(
        self,
        messenger: MessengerAdapter,
        api: IntegrationGateway,
        translator: Translator,
    ):
        self.messenger = messenger
        self.api = api
        self.translator = translator

        self.selection_handlers: Final[
            dict[VerificationInteraction, Callable[[OptionSelection], Awaitable[None]]]
        ] = {VerificationInteraction.ACCOUNT_LINKING: self._handle_account_linking}

    async def ask_for_confirmation(
        self, chat_id: int, request_id: str, interaction: VerificationInteraction
    ):
        prompt = ChoicePrompt(
            id=request_id,
            text_key=TranslationKey.AUTH_ACCOUNT_LINKAGE_TEXT,
            interaction=interaction,
            choices=[
                Choice(self.CHOICE_ACCEPT, TranslationKey.PROMPT_ACCEPT),
                Choice(self.CHOICE_REJECT, TranslationKey.PROMPT_REJECT),
            ],
        )

        await self.messenger.send_choice_prompt(chat_id, prompt)

    async def handle_selection(self, selection: OptionSelection):
        handler = self.selection_handlers.get(selection.interaction)
        if handler is None:
            logger.error(
                "No handler registered for interaction: %s", selection.interaction
            )
            return
        await handler(selection)

    async def _handle_account_linking(self, selection: OptionSelection):
        if selection.value not in (self.CHOICE_ACCEPT, self.CHOICE_REJECT):
            logger.error("Unknown account-linking choice value: %s", selection.value)
            return

        is_accepted = selection.value == self.CHOICE_ACCEPT

        result = await self.api.link_messenger_account(
            request_id=selection.prompt_id,
            is_accepted=is_accepted,
        )

        def edit_message_text(_: str):
            # TODO: Consider format {original}\n\nUPD: {result}
            return self.translator.translate_response(result)

        await self.messenger.edit_message(
            selection.chat_id,
            selection.message_id,
            edit_message_text,
        )
