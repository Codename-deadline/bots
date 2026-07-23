from common.application.arg_parsers import (
    ArgParseError,
    parse_chat_args,
)
from common.application.protocols.integration_gateway import (
    ChatPreferences,
    ChatPreferenceUpdates,
    IntegrationGateway,
)
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

        parsed_args = parse_chat_args(command.args, require_all=True)
        if parsed_args.error is not None:
            await self._reply_parse_error(command, parsed_args.error)
            return
        args = parsed_args.as_required_value()
        if args.language is None or args.time_zone is None:
            raise ValueError("Required registration arguments were not parsed")

        res = await self.api.register_chat(
            command.message.account_id,
            command.message.chat_id,
            command.message.chat_title,
            ChatPreferences(args.language, args.time_zone),
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
        parsed_args = parse_chat_args(command.args, require_all=False)
        if parsed_args.error is not None:
            await self._reply_parse_error(command, parsed_args.error)
            return
        args = parsed_args.as_required_value()

        res = await self.api.update_chat_info(
            command.message.account_id,
            command.message.chat_id,
            command.message.has_chat_admin_rights,
            command.message.chat_title,
            ChatPreferenceUpdates(args.language, args.time_zone),
        )
        await self.messenger.reply_to_message(
            command.message.chat_id,
            command.message.id,
            self.translator.translate_response(res),
        )
