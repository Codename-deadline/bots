from typing import Literal

from common.application.arg_parsers import ArgParseError, parse_required_int
from common.application.protocols.integration_gateway import (
    IntegrationGateway,
    ScopeType,
)
from common.application.protocols.messenger_adapter import MessengerAdapter
from common.application.protocols.translator import Translator
from common.contracts.incoming_command import CommandName, IncomingCommand


class SubscriptionService:
    SCOPE_TYPE_TO_COMMAND: dict[
        Literal["sub", "unsub"], dict[ScopeType, CommandName]
    ] = {
        "sub": {
            ScopeType.ORGANIZATION: CommandName.SUBSCRIBE_TO_ORGANIZATION,
            ScopeType.THREAD: CommandName.SUBSCRIBE_TO_THREAD,
            ScopeType.DEADLINE: CommandName.SUBSCRIBE_TO_DEADLINE,
        },
        "unsub": {
            ScopeType.ORGANIZATION: CommandName.UNSUBSCRIBE_FROM_ORGANIZATION,
            ScopeType.THREAD: CommandName.UNSUBSCRIBE_FROM_THREAD,
            ScopeType.DEADLINE: CommandName.UNSUBSCRIBE_FROM_DEADLINE,
        },
    }

    def _resolve_command_name_from_scope_type(
        self, prefix: Literal["sub", "unsub"], scope_type: ScopeType
    ) -> CommandName:
        return self.SCOPE_TYPE_TO_COMMAND[prefix][scope_type]

    def __init__(
        self,
        messenger: MessengerAdapter,
        api: IntegrationGateway,
        translator: Translator,
    ):
        self.messenger = messenger
        self.api = api
        self.translator = translator

    async def _reply_parse_error(
        self, command: IncomingCommand, error: ArgParseError
    ) -> None:
        await self.messenger.reply_to_message(
            command.message.chat_id,
            command.message.id,
            self.translator.translate(error.message_key, command.message.language),
        )

    async def subscribe_to(self, command: IncomingCommand, scope_type: ScopeType):
        command.match_or_raise(
            self._resolve_command_name_from_scope_type("sub", scope_type)
        )

        scope_id = parse_required_int(command.args)
        if scope_id.error is not None:
            await self._reply_parse_error(command, scope_id.error)
            return

        res = await self.api.subscribe_to_scope(
            scope_type,
            command.message.account_id,
            scope_id.as_required_value(),
            command.message.chat_id,
            command.message.has_chat_admin_rights,
        )

        await self.messenger.reply_to_message(
            command.message.chat_id,
            command.message.id,
            self.translator.translate_response(res),
        )

    async def unsubscribe_from(self, command: IncomingCommand, scope_type: ScopeType):
        command.match_or_raise(
            self._resolve_command_name_from_scope_type("unsub", scope_type)
        )

        scope_id = parse_required_int(command.args)
        if scope_id.error is not None:
            await self._reply_parse_error(command, scope_id.error)
            return

        res = await self.api.unsubscribe_from_scope(
            scope_type,
            command.message.account_id,
            scope_id.as_required_value(),
            command.message.chat_id,
            command.message.has_chat_admin_rights,
        )
        await self.messenger.reply_to_message(
            command.message.chat_id,
            command.message.id,
            self.translator.translate_response(res),
        )

    async def unsubscribe_from_all(self, command: IncomingCommand):
        command.match_or_raise(CommandName.UNSUBSCRIBE_FROM_ALL)

        res = await self.api.unsubscribe_from_all(
            command.message.account_id,
            command.message.chat_id,
            command.message.has_chat_admin_rights,
        )

        await self.messenger.reply_to_message(
            command.message.chat_id,
            command.message.id,
            self.translator.translate_response(res),
        )
