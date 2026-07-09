from typing import Literal

from common.application.arg_parsers import ArgParseResult, parse_required_int
from common.application.protocols.integration_gateway import (
    IntegrationGateway,
    ScopeType,
)
from common.application.protocols.messenger_adapter import MessengerAdapter
from common.contracts.incoming_command import CommandName, IncomingCommand
from common.infrastructure.i18n.i18n import format_with_locale


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

    def __init__(self, messenger: MessengerAdapter, api: IntegrationGateway):
        self.messenger = messenger
        self.api = api

    async def subscribe_to(self, command: IncomingCommand, scope_type: ScopeType):
        command.match_or_raise(
            self._resolve_command_name_from_scope_type("sub", scope_type)
        )

        scope_id: ArgParseResult[int] = parse_required_int(command.args)
        if not scope_id.ok:
            # TODO: Error
            return

        res = await self.api.subscribe_to_scope(
            scope_type,
            command.message.account_id,
            scope_id.as_required_value(),
            command.message.chat_id,
        )

        await self.messenger.reply_to_message(
            command.message.chat_id, command.message.id, format_with_locale(res)
        )

    async def unsubscribe_from(self, command: IncomingCommand, scope_type: ScopeType):
        command.match_or_raise(
            self._resolve_command_name_from_scope_type("unsub", scope_type)
        )

        scope_id: ArgParseResult[int] = parse_required_int(command.args)
        if not scope_id.ok:
            # TODO: Error
            return

        res = await self.api.unsubscribe_from_scope(
            scope_type,
            command.message.account_id,
            scope_id.as_required_value(),
            command.message.chat_id,
        )
        # if res.is_error:
        #     self.__logger.error("[Unsub]: %s", res.key)

        await self.messenger.reply_to_message(
            command.message.chat_id, command.message.id, format_with_locale(res)
        )

    async def unsubscribe_from_all(self, command: IncomingCommand):
        command.match_or_raise(CommandName.UNSUBSCRIBE_FROM_ALL)

        res = await self.api.unsubscribe_from_all(
            command.message.account_id, command.message.chat_id
        )

        await self.messenger.reply_to_message(
            command.message.chat_id, command.message.id, format_with_locale(res)
        )
