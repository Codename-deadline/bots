from collections.abc import Awaitable, Callable
from typing import Final

from common.application.protocols.integration_gateway import IntegrationGateway
from common.application.protocols.messenger_adapter import MessengerAdapter
from common.contracts.choice.choice import Choice
from common.contracts.choice.choice_prompt import ChoicePrompt
from common.contracts.choice.option_selection import OptionSelection
from common.contracts.interaction import VerificationInteraction


class VerificationService:
    CHOICE_ACCEPT: Final[str] = "accept"
    CHOICE_REJECT: Final[str] = "reject"

    def __init__(self, messenger: MessengerAdapter, api: IntegrationGateway):
        self.messenger = messenger
        self.api = api

        self.selection_handlers: Final[
            dict[VerificationInteraction, Callable[[OptionSelection], Awaitable[None]]]
        ] = {VerificationInteraction.ACCOUNT_LINKING: self.handle_selection}

    async def ask_for_confirmation(
        self, chat_id: int, request_id: str, interaction: VerificationInteraction
    ):
        prompt = ChoicePrompt(
            id=request_id,
            text="Do you want to link this account?",
            interaction=interaction.value,
            choices=[
                Choice(self.CHOICE_ACCEPT, "Yes"),
                Choice(self.CHOICE_REJECT, "No"),
            ],
        )

        await self.messenger.send_choice_prompt(chat_id, prompt)

    async def handle_selection(self, selection: OptionSelection):
        try:
            interaction = VerificationInteraction(selection.interaction)
        except ValueError:
            # TODO log error
            return

        handler = self.selection_handlers.get(interaction)
        if handler is None:
            # TODO: log error
            return
        await handler(selection)

    async def _handle_account_linking(self, selection: OptionSelection):
        is_accepted: bool = selection.value == self.CHOICE_ACCEPT

        result = await self.api.link_messenger_account(
            request_id=selection.request_id,
            is_accepted=is_accepted,
        )

        def edit_message_text(_: str):
            # TODO: i18n
            return result.key

        await self.messenger.edit_message(
            selection.chat_id,
            selection.message_id,
            edit_message_text,
        )
