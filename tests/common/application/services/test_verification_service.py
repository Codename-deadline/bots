from common.application.enums import Language
from common.application.services.verification_service import VerificationService
from common.application.translation import TranslationKey
from common.contracts.choice.option_selection import OptionSelection
from common.contracts.interaction import VerificationInteraction
from tests.common.application.services.fakes import (
    FakeIntegrationGateway,
    FakeMessenger,
    FakeTranslator,
)


async def test_ask_for_confirmation_sends_i18n_backed_prompt():
    messenger = FakeMessenger()
    service = VerificationService(messenger, FakeIntegrationGateway(), FakeTranslator())

    await service.ask_for_confirmation(
        10, "request-1", VerificationInteraction.ACCOUNT_LINKING
    )

    assert len(messenger.prompts) == 1
    chat_id, prompt, options_per_line = messenger.prompts[0]
    assert chat_id == 10
    assert options_per_line == 2
    assert prompt.id == "request-1"
    assert prompt.text_key == TranslationKey.AUTH_ACCOUNT_LINKAGE_TEXT
    assert prompt.interaction == VerificationInteraction.ACCOUNT_LINKING
    assert [choice.label_key for choice in prompt.choices] == [
        TranslationKey.PROMPT_ACCEPT,
        TranslationKey.PROMPT_REJECT,
    ]


async def test_handle_account_linking_accepts_selection():
    messenger = FakeMessenger()
    api = FakeIntegrationGateway()
    service = VerificationService(messenger, api, FakeTranslator())
    selection = OptionSelection(
        prompt_id="request-1",
        account_id=20,
        chat_id=30,
        message_id=40,
        interaction=VerificationInteraction.ACCOUNT_LINKING,
        value="accept",
    )

    await service.handle_selection(selection)

    assert api.calls == [("link_messenger_account", "request-1", True, 20)]
    assert messenger.edits == [(30, 40, f"{Language.EN}:register_chat.success")]


async def test_handle_account_linking_rejects_selection():
    messenger = FakeMessenger()
    api = FakeIntegrationGateway()
    service = VerificationService(messenger, api, FakeTranslator())
    selection = OptionSelection(
        prompt_id="request-1",
        account_id=20,
        chat_id=30,
        message_id=40,
        interaction=VerificationInteraction.ACCOUNT_LINKING,
        value="reject",
    )

    await service.handle_selection(selection)

    assert api.calls == [("link_messenger_account", "request-1", False, 20)]


async def test_handle_account_linking_keeps_prompt_on_retryable_error():
    messenger = FakeMessenger()
    api = FakeIntegrationGateway()
    api.response = api.response.__class__(
        is_error=True,
        is_retryable=True,
        key="errors.server_unavailable",
        language=Language.EN,
    )
    service = VerificationService(messenger, api, FakeTranslator())
    selection = OptionSelection(
        prompt_id="request-1",
        account_id=20,
        chat_id=30,
        message_id=40,
        interaction=VerificationInteraction.ACCOUNT_LINKING,
        value="accept",
    )

    await service.handle_selection(selection)

    assert messenger.edits == []
    assert messenger.replies == [(30, 40, f"{Language.EN}:errors.server_unavailable")]


async def test_handle_account_linking_ignores_unknown_choice():
    messenger = FakeMessenger()
    api = FakeIntegrationGateway()
    service = VerificationService(messenger, api, FakeTranslator())
    selection = OptionSelection(
        prompt_id="request-1",
        account_id=20,
        chat_id=30,
        message_id=40,
        interaction=VerificationInteraction.ACCOUNT_LINKING,
        value="maybe",
    )

    await service.handle_selection(selection)

    assert api.calls == []
    assert messenger.edits == []
