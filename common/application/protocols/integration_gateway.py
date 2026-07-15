from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from common.application.enums import Language


@dataclass(frozen=True)
class IntegrationResponse:
    is_error: bool
    key: str
    language: Language
    is_retryable: bool = False


class ScopeType(StrEnum):
    ORGANIZATION = "org"
    THREAD = "thr"
    DEADLINE = "ddl"


class IntegrationGateway(Protocol):
    async def link_messenger_account(
        self, request_id: str, is_accepted: bool, account_id: int
    ) -> IntegrationResponse: ...

    async def register_chat(
        self,
        account_id: int,
        chat_id: int,
        chat_title: str,
        language: Language,
        is_admin: bool,
    ) -> IntegrationResponse: ...
    async def deregister_chat(
        self,
        account_id: int,
        chat_id: int,
        is_admin: bool,
    ) -> IntegrationResponse: ...

    async def update_chat_info(
        self,
        account_id: int,
        chat_id: int,
        is_admin: bool,
        chat_title: str,
        language: Language | None,
    ) -> IntegrationResponse: ...

    async def subscribe_to_scope(
        self,
        scope_type: ScopeType,
        account_id: int,
        scope_id: int,
        chat_id: int,
        is_admin: bool,
    ) -> IntegrationResponse: ...
    async def unsubscribe_from_scope(
        self,
        scope_type: ScopeType,
        account_id: int,
        scope_id: int,
        chat_id: int,
        is_admin: bool,
    ) -> IntegrationResponse: ...
    async def unsubscribe_from_all(
        self, account_id: int, chat_id: int, is_admin: bool
    ) -> IntegrationResponse: ...
