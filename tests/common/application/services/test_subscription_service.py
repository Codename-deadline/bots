from common.application.enums import Language
from common.application.protocols.integration_gateway import ScopeType
from common.application.services.subscription_service import SubscriptionService
from common.application.translation import TranslationKey
from common.contracts.incoming_command import CommandName, IncomingCommand
from common.contracts.incoming_message import IncomingMessage
from tests.common.application.services.fakes import (
    FakeIntegrationGateway,
    FakeMessenger,
    FakeTranslator,
)


def _command(name: CommandName, args: tuple[str, ...]) -> IncomingCommand:
    return IncomingCommand(
        IncomingMessage(
            id=10,
            account_id=20,
            chat_id=30,
            chat_title="Chat",
            text="",
            language=Language.EN,
            is_private=False,
            has_chat_admin_rights=True,
        ),
        name,
        args,
    )


async def test_subscribe_to_scope_calls_api():
    messenger = FakeMessenger()
    api = FakeIntegrationGateway()
    service = SubscriptionService(messenger, api, FakeTranslator())

    await service.subscribe_to(
        _command(CommandName.SUBSCRIBE_TO_ORGANIZATION, ("42",)),
        ScopeType.ORGANIZATION,
    )

    assert api.calls == [
        ("subscribe_to_scope", ScopeType.ORGANIZATION, 20, 42, 30, True)
    ]


async def test_subscribe_to_scope_replies_validation_error_without_api_call():
    messenger = FakeMessenger()
    api = FakeIntegrationGateway()
    service = SubscriptionService(messenger, api, FakeTranslator())

    await service.subscribe_to(
        _command(CommandName.SUBSCRIBE_TO_ORGANIZATION, ("abc",)),
        ScopeType.ORGANIZATION,
    )

    assert api.calls == []
    assert messenger.replies == [
        (
            30,
            10,
            f"{Language.EN}:{TranslationKey.VALIDATION_INVALID_COMMAND_FORMAT.value}",
        )
    ]


async def test_unsubscribe_from_all_calls_api_without_args():
    messenger = FakeMessenger()
    api = FakeIntegrationGateway()
    service = SubscriptionService(messenger, api, FakeTranslator())

    await service.unsubscribe_from_all(_command(CommandName.UNSUBSCRIBE_FROM_ALL, ()))

    assert api.calls == [("unsubscribe_from_all", 20, 30, True)]
