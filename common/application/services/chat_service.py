from common.application.arg_parsers import (
    ArgParseError,
    parse_optional_language,
    parse_required_language,
)
from common.application.protocols.integration_gateway import IntegrationGateway
from common.application.protocols.messenger_adapter import MessengerAdapter
from common.application.protocols.translator import Translator
from common.contracts.incoming_command import CommandName, IncomingCommand


class ChatService:
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

    async def register_chat(self, command: IncomingCommand):
        command.match_or_raise(CommandName.REGISTER_CHAT)

        parsed_language = parse_required_language(command.args)
        if parsed_language.error is not None:
            await self._reply_parse_error(command, parsed_language.error)
            return

        res = await self.api.register_chat(
            command.message.account_id,
            command.message.chat_id,
            command.message.chat_title,
            parsed_language.as_required_value(),
            command.message.has_chat_admin_rights,
        )
        await self.messenger.reply_to_message(
            command.message.chat_id,
            command.message.id,
            self.translator.translate_response(res),
        )

    async def deregister_chat(self, command: IncomingCommand):
        command.match_or_raise(CommandName.DEREGISTER_CHAT)

        res = await self.api.deregister_chat(
            command.message.account_id,
            command.message.chat_id,
            command.message.has_chat_admin_rights,
        )
        await self.messenger.reply_to_message(
            command.message.chat_id,
            command.message.id,
            self.translator.translate_response(res),
        )

    async def update_chat_info(self, command: IncomingCommand):
        command.match_or_raise(CommandName.UPDATE_CHAT_INFO)
        parsed_language = parse_optional_language(command.args)
        if parsed_language.error is not None:
            await self._reply_parse_error(command, parsed_language.error)
            return

        res = await self.api.update_chat_info(
            command.message.account_id,
            command.message.chat_id,
            command.message.has_chat_admin_rights,
            command.message.chat_title,
            parsed_language.as_optional_value(),
        )
        await self.messenger.reply_to_message(
            command.message.chat_id,
            command.message.id,
            self.translator.translate_response(res),
        )
