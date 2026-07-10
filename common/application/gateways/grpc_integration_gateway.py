import logging
from typing import cast

import grpc
from grpc import StatusCode
from grpc.aio import Channel

from common.application.enums import Language, Messenger
from common.application.protocols.integration_gateway import (
    IntegrationGateway,
    IntegrationResponse,
    ScopeType,
)
from common.config.bot_config import config
from common.infrastructure.grpc.generated import integration_pb2, integration_pb2_grpc

logger = logging.getLogger(__name__)


class GrpcIntegrationGateway(IntegrationGateway):
    _channel: Channel
    _integration_service: integration_pb2_grpc.IntegrationServiceStub

    def __init__(  # noqa: PLR0913
        self,
        target: str,
        messenger: Messenger,
        bot_id: int,
        is_secure: bool = False,
        credentials=None,
        timeout: float = 5.0,
    ):
        self._target: str = target
        self._is_secure: bool = is_secure
        self._credentials = credentials
        self._timeout: float = timeout
        self._messenger: integration_pb2.ProtoMessenger = getattr(
            integration_pb2, messenger.name
        )
        self._bot_id: int = bot_id

    async def start(self):
        """Open channel and instantiate stubs. Call at app startup."""
        if self._is_secure:
            assert self._credentials is not None
            self._channel = grpc.aio.secure_channel(self._target, self._credentials)
        else:
            self._channel = grpc.aio.insecure_channel(self._target)

        self._integration_service = integration_pb2_grpc.IntegrationServiceStub(
            self._channel
        )

        # TODO: Add health check

    async def close(self):
        await self._channel.close()

    # rpc_error_callback:
    # Callable[[StatusCode, str], Awaitable[None]] = lambda x, y: None
    async def __call_with_defaults(
        self, method, request, timeout=None, metadata=None
    ) -> IntegrationResponse:
        """Generic wrapper that applies default timeout & metadata."""
        if timeout is None:
            timeout = self._timeout
        try:
            res = cast(
                integration_pb2.GeneralResponse,
                await method(request, timeout=timeout, metadata=metadata),
            )
            return IntegrationResponse(
                is_error=False,
                key=res.key,
                language=Language(integration_pb2.Locale.Name(res.locale)),
            )
        except grpc.RpcError as rpc_error:
            e = cast(grpc.aio.AioRpcError, rpc_error)
            logger.error(
                "gRPC error occurred. status=%s details=%s",
                e.code(),
                e.details(),
            )

            error_message_key: str = (
                (e.details() or "errors.error")
                if e.code() != StatusCode.UNAVAILABLE
                else "errors.server_unavailable"
            )
            metadata_locale = None
            for key, value in e.trailing_metadata() or ():
                if key == "locale":
                    metadata_locale = value
                    break

            return IntegrationResponse(
                is_error=True,
                key=error_message_key,
                language=Language(metadata_locale or config.fallback_language.name),
            )

    async def link_messenger_account(self, request_id: str, is_accepted: bool):
        request = integration_pb2.LinkMessengerAccountRequest(
            request_id=request_id, is_accepted=is_accepted
        )
        return await self.__call_with_defaults(
            self._integration_service.LinkMessengerAccount, request
        )

    async def _subscribe_to(
        self, account_id: int, target_id: int, chat_id: int, grpc_callable
    ):
        request = integration_pb2.SubscribeToRequest(
            issuer_messenger_account_id=account_id,
            target_id=target_id,
            messenger_chat_id=chat_id,
            messenger=self._messenger,
        )
        return await self.__call_with_defaults(grpc_callable, request)

    async def subscribe_to_scope(
        self, scope_type: ScopeType, account_id: int, scope_id: int, chat_id: int
    ):
        match scope_type:
            case ScopeType.ORGANIZATION:
                return await self._subscribe_to(
                    account_id,
                    scope_id,
                    chat_id,
                    self._integration_service.SubscribeToOrganization,
                )
            case ScopeType.THREAD:
                return await self._subscribe_to(
                    account_id,
                    scope_id,
                    chat_id,
                    self._integration_service.SubscribeToThread,
                )
            case ScopeType.DEADLINE:
                return await self._subscribe_to(
                    account_id,
                    scope_id,
                    chat_id,
                    self._integration_service.SubscribeToDeadline,
                )

    async def _unsubscribe_from(
        self, account_id: int, target_id: int, chat_id: int, grpc_callable
    ):
        request = integration_pb2.UnsubscribeFromRequest(
            issuer_messenger_account_id=account_id,
            target_id=target_id,
            messenger_chat_id=chat_id,
            messenger=self._messenger,
        )
        return await self.__call_with_defaults(grpc_callable, request)

    async def unsubscribe_from_scope(
        self, scope_type: ScopeType, account_id: int, scope_id: int, chat_id: int
    ):
        match scope_type:
            case ScopeType.ORGANIZATION:
                return await self._unsubscribe_from(
                    account_id,
                    scope_id,
                    chat_id,
                    self._integration_service.UnsubscribeFromOrganization,
                )
            case ScopeType.THREAD:
                return await self._unsubscribe_from(
                    account_id,
                    scope_id,
                    chat_id,
                    self._integration_service.UnsubscribeFromThread,
                )
            case ScopeType.DEADLINE:
                return await self._unsubscribe_from(
                    account_id,
                    scope_id,
                    chat_id,
                    self._integration_service.UnsubscribeFromDeadline,
                )

    async def unsubscribe_from_all(self, account_id: int, chat_id: int):
        request = integration_pb2.UnsubscribeFromAllRequest(
            issuer_messenger_account_id=account_id,
            messenger_chat_id=chat_id,
            messenger=self._messenger,
        )
        return await self.__call_with_defaults(
            self._integration_service.UnsubscribeFromAll, request
        )

    async def register_chat(
        self,
        account_id: int,
        chat_id: int,
        chat_title: str,
        language: Language,
        is_admin: bool,
    ):
        request = integration_pb2.RegisterChatRequest(
            bot_id=self._bot_id,
            issuer_messenger_account_id=account_id,
            messenger=self._messenger,
            messenger_chat_id=chat_id,
            chat_title=chat_title,
            language=language.value,
            issuer_has_messenger_chat_admin_rights=is_admin,
        )
        return await self.__call_with_defaults(
            self._integration_service.RegisterChat, request
        )

    async def deregister_chat(
        self,
        account_id: int,
        chat_id: int,
        is_admin: bool,
    ):
        return await self.__call_with_defaults(
            self._integration_service.DeregisterChat,
            integration_pb2.DeregisterChatRequest(
                messenger_chat_id=chat_id,
                messenger=self._messenger,
                issuer_messenger_account_id=account_id,
                issuer_has_messenger_chat_admin_rights=is_admin,
            ),
        )

    async def update_chat_info(
        self,
        account_id: int,
        chat_id: int,
        is_admin: bool,
        chat_title: str,
        language: Language | None,
    ):
        request = integration_pb2.UpdateChatInfoRequest(
            issuer_messenger_account_id=account_id,
            messenger=self._messenger,
            messenger_chat_id=chat_id,
            language=language,
            title=chat_title,
            issuer_has_messenger_chat_admin_rights=is_admin,
        )
        return await self.__call_with_defaults(
            self._integration_service.UpdateChatInfo, request
        )
