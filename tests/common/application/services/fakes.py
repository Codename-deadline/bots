from common.application.enums import Language
from common.application.protocols.integration_gateway import IntegrationResponse
from common.application.translation import TranslationKey


class FakeMessenger:
    def __init__(self):
        self.messages = []
        self.replies = []
        self.edits = []
        self.prompts = []

    async def send_message(self, chat_id: int, text: str) -> None:
        self.messages.append((chat_id, text))

    async def reply_to_message(self, chat_id: int, message_id: int, text: str) -> None:
        self.replies.append((chat_id, message_id, text))

    async def edit_message(self, chat_id: int, message_id: int, update) -> None:
        self.edits.append((chat_id, message_id, update("original")))

    async def send_choice_prompt(self, chat_id: int, options) -> None:
        self.prompts.append((chat_id, options))


class FakeIntegrationGateway:
    def __init__(self):
        self.calls = []
        self.response = IntegrationResponse(
            is_error=False,
            key=TranslationKey.REGISTER_CHAT_SUCCESS.value,
            language=Language.EN,
        )

    async def link_messenger_account(self, request_id: str, is_accepted: bool):
        self.calls.append(("link_messenger_account", request_id, is_accepted))
        return self.response

    async def register_chat(
        self, account_id: int, chat_id: int, chat_title: str, language, is_admin: bool
    ):
        self.calls.append(
            ("register_chat", account_id, chat_id, chat_title, language, is_admin)
        )
        return self.response

    async def deregister_chat(self, account_id: int, chat_id: int, is_admin: bool):
        self.calls.append(("deregister_chat", account_id, chat_id, is_admin))
        return self.response

    async def update_chat_info(
        self, account_id: int, chat_id: int, is_admin: bool, chat_title: str, language
    ):
        self.calls.append(
            ("update_chat_info", account_id, chat_id, is_admin, chat_title, language)
        )
        return self.response

    async def subscribe_to_scope(
        self, scope_type, account_id: int, scope_id: int, chat_id: int
    ):
        self.calls.append(
            ("subscribe_to_scope", scope_type, account_id, scope_id, chat_id)
        )
        return self.response

    async def unsubscribe_from_scope(
        self, scope_type, account_id: int, scope_id: int, chat_id: int
    ):
        self.calls.append(
            ("unsubscribe_from_scope", scope_type, account_id, scope_id, chat_id)
        )
        return self.response

    async def unsubscribe_from_all(self, account_id: int, chat_id: int):
        self.calls.append(("unsubscribe_from_all", account_id, chat_id))
        return self.response


class FakeTranslator:
    def translate(
        self, key: TranslationKey, language: Language | None = None, **params
    ):
        return f"{language or 'fallback'}:{key.value}"

    def translate_response(self, response: IntegrationResponse, **params):
        return f"{response.language}:{response.key}"
