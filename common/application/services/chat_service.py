from common.application.arg_parsers import (
    ArgParseResult,
    parse_optional_language,
    parse_required_language,
)
from common.application.enums import Language
from common.application.protocols.integration_gateway import IntegrationGateway
from common.application.protocols.messenger_adapter import MessengerAdapter
from common.contracts.incoming_command import CommandName, IncomingCommand
from common.infrastructure.i18n.i18n import format_with_locale


class ChatService:
    def __init__(self, messenger: MessengerAdapter, api: IntegrationGateway):
        self.messenger = messenger
        self.api = api

    async def register_chat(self, command: IncomingCommand):
        command.match_or_raise(CommandName.REGISTER_CHAT)

        language: ArgParseResult[Language] = parse_required_language(command.args)
        if not language.ok:
            # TODO
            return

        res = await self.api.register_chat(
            command.message.account_id,
            command.message.chat_id,
            command.message.chat_title,
            language.as_required_value(),
            command.message.has_chat_admin_rights,
        )
        await self.messenger.reply_to_message(
            command.message.chat_id, command.message.id, format_with_locale(res)
        )

    async def deregister_chat(self, command: IncomingCommand):
        command.match_or_raise(CommandName.DEREGISTER_CHAT)

        res = await self.api.deregister_chat(
            command.message.account_id,
            command.message.chat_id,
            command.message.has_chat_admin_rights,
        )
        await self.messenger.reply_to_message(
            command.message.chat_id, command.message.id, format_with_locale(res)
        )

    async def update_chat_info(self, command: IncomingCommand):
        command.match_or_raise(CommandName.UPDATE_CHAT_INFO)
        parsed_language: ArgParseResult[Language] = parse_optional_language(
            command.args
        )
        if not parsed_language.ok:
            await self.messenger.reply_to_message(
                command.message.chat_id,
                command.message.id,
                format_with_locale("validation.unsupported_language"),
            )
            return

        res = await self.api.update_chat_info(
            command.message.account_id,
            command.message.chat_id,
            command.message.has_chat_admin_rights,
            command.message.chat_title,
            parsed_language.as_optional_value(),
        )
        await self.messenger.reply_to_message(
            command.message.chat_id, command.message.id, format_with_locale(res)
        )
