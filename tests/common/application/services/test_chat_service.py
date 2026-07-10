from common.application.enums import Language
from common.application.services.chat_service import ChatService
from common.application.translation import TranslationKey
from common.contracts.incoming_command import CommandName, IncomingCommand
from common.contracts.incoming_message import IncomingMessage
from tests.common.application.services.fakes import (
    FakeIntegrationGateway,
    FakeMessenger,
    FakeTranslator,
)


def _message() -> IncomingMessage:
    return IncomingMessage(
        id=10,
        account_id=20,
        chat_id=30,
        chat_title="Chat",
        text="",
        language=Language.EN,
        is_private=False,
        has_chat_admin_rights=True,
    )


async def test_register_chat_calls_api_and_replies():
    messenger = FakeMessenger()
    api = FakeIntegrationGateway()
    service = ChatService(messenger, api, FakeTranslator())
    command = IncomingCommand(_message(), CommandName.REGISTER_CHAT, ("en",))

    await service.register_chat(command)

    assert api.calls == [("register_chat", 20, 30, "Chat", Language.EN, True)]
    assert messenger.replies == [(10 + 20, 10, "EN:register_chat.success")]


async def test_register_chat_replies_validation_error_without_api_call():
    messenger = FakeMessenger()
    api = FakeIntegrationGateway()
    service = ChatService(messenger, api, FakeTranslator())
    command = IncomingCommand(_message(), CommandName.REGISTER_CHAT, ("de",))

    await service.register_chat(command)

    assert api.calls == []
    assert messenger.replies == [
        (
            30,
            10,
            f"{Language.EN}:{TranslationKey.VALIDATION_UNSUPPORTED_LANGUAGE.value}",
        )
    ]


async def test_update_chat_info_allows_missing_language():
    messenger = FakeMessenger()
    api = FakeIntegrationGateway()
    service = ChatService(messenger, api, FakeTranslator())
    command = IncomingCommand(_message(), CommandName.UPDATE_CHAT_INFO, ())

    await service.update_chat_info(command)

    assert api.calls == [("update_chat_info", 20, 30, True, "Chat", None)]


async def test_deregister_chat_calls_api():
    messenger = FakeMessenger()
    api = FakeIntegrationGateway()
    service = ChatService(messenger, api, FakeTranslator())
    command = IncomingCommand(_message(), CommandName.DEREGISTER_CHAT, ())

    await service.deregister_chat(command)

    assert api.calls == [("deregister_chat", 20, 30, True)]
