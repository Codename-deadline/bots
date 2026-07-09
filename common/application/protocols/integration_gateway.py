from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from common.application.enums import Language


@dataclass(frozen=True)
class GrpcResponse:
    is_error: bool
    key: str
    language: Language


class ScopeType(StrEnum):
    ORGANIZATION = "org"
    THREAD = "thr"
    DEADLINE = "ddl"


class IntegrationGateway(Protocol):
    async def link_messenger_account(
        self, request_id: str, is_accepted: bool
    ) -> GrpcResponse: ...

    async def register_chat(
        self,
        account_id: int,
        chat_id: int,
        chat_title: str,
        language: Language,
        is_admin: bool,
    ) -> GrpcResponse: ...
    async def deregister_chat(
        self,
        account_id: int,
        chat_id: int,
        is_admin: bool,
    ) -> GrpcResponse: ...

    async def update_chat_info(
        self,
        account_id: int,
        chat_id: int,
        is_admin: bool,
        chat_title: str,
        language: Language | None,
    ) -> GrpcResponse: ...

    async def subscribe_to_scope(
        self, scope_type: ScopeType, account_id: int, scope_id: int, chat_id: int
    ) -> GrpcResponse: ...
    async def unsubscribe_from_scope(
        self, scope_type: ScopeType, account_id: int, scope_id: int, chat_id: int
    ) -> GrpcResponse: ...
    async def unsubscribe_from_all(
        self, account_id: int, chat_id: int
    ) -> GrpcResponse: ...
