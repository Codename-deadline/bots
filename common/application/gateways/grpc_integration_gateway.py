import logging
from typing import cast

import grpc
from grpc import StatusCode
from grpc.aio import Channel

from common.application.enums import Language, Messenger
from common.application.protocols.integration_gateway import (
    ChatPreferences,
    ChatPreferenceUpdates,
    IntegrationGateway,
    IntegrationResponse,
    ScopeType,
)
from common.config.schemas.grpc_config import GrpcConfig
from common.infrastructure.grpc.generated import integration_pb2, integration_pb2_grpc

logger = logging.getLogger(__name__)


class GrpcIntegrationGateway(IntegrationGateway):
    _channel: Channel
    _integration_service: integration_pb2_grpc.IntegrationServiceStub

    def __init__(
        self,
        config: GrpcConfig,
        bot_id: int,
        messenger: Messenger,
        fallback_language: Language,
    ):
        self._target: str = config.target
        self._tls_paths = config.tls.credentials_paths if config.tls.enabled else None
        self._timeout: float = config.timeout
        self._fallback_language = fallback_language
        self._messenger: integration_pb2.ProtoMessenger = getattr(
            integration_pb2, messenger.name
        )
        self._bot_id: int = bot_id

    async def start(self):
        """Open channel and instantiate stubs. Call at app startup."""
        if self._tls_paths is not None:
            credentials = grpc.ssl_channel_credentials(
                root_certificates=self._tls_paths.ca_certificate.read_bytes(),
                private_key=self._tls_paths.private_key.read_bytes(),
                certificate_chain=self._tls_paths.certificate.read_bytes(),
            )
            self._channel = grpc.aio.secure_channel(self._target, credentials)
        else:
            self._channel = grpc.aio.insecure_channel(self._target)

        self._integration_service = integration_pb2_grpc.IntegrationServiceStub(
            self._channel
        )

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
                language=Language(metadata_locale or self._fallback_language.name),
                is_retryable=e.code()
                in (StatusCode.UNAVAILABLE, StatusCode.DEADLINE_EXCEEDED),
            )

    async def link_messenger_account(
        self, request_id: str, is_accepted: bool, account_id: int
    ):
        request = integration_pb2.LinkMessengerAccountRequest(
            request_id=request_id,
            is_accepted=is_accepted,
            messenger_account_id=account_id,
            messenger=self._messenger,
        )
        return await self.__call_with_defaults(
            self._integration_service.LinkMessengerAccount, request
        )

    async def _subscribe_to(
        self,
        account_id: int,
        target_id: int,
        chat_id: int,
        is_admin: bool,
        grpc_callable,
    ):
        request = integration_pb2.SubscribeToRequest(
            issuer_messenger_account_id=account_id,
            target_id=target_id,
            messenger_chat_id=chat_id,
            messenger=self._messenger,
            issuer_has_messenger_chat_admin_rights=is_admin,
        )
        return await self.__call_with_defaults(grpc_callable, request)

    async def subscribe_to_scope(
        self,
        scope_type: ScopeType,
        account_id: int,
        scope_id: int,
        chat_id: int,
        is_admin: bool,
    ):
        match scope_type:
            case ScopeType.ORGANIZATION:
                return await self._subscribe_to(
                    account_id,
                    scope_id,
                    chat_id,
                    is_admin,
                    self._integration_service.SubscribeToOrganization,
                )
            case ScopeType.THREAD:
                return await self._subscribe_to(
                    account_id,
                    scope_id,
                    chat_id,
                    is_admin,
                    self._integration_service.SubscribeToThread,
                )
            case ScopeType.DEADLINE:
                return await self._subscribe_to(
                    account_id,
                    scope_id,
                    chat_id,
                    is_admin,
                    self._integration_service.SubscribeToDeadline,
                )

    async def _unsubscribe_from(
        self,
        account_id: int,
        target_id: int,
        chat_id: int,
        is_admin: bool,
        grpc_callable,
    ):
        request = integration_pb2.UnsubscribeFromRequest(
            issuer_messenger_account_id=account_id,
            target_id=target_id,
            messenger_chat_id=chat_id,
            messenger=self._messenger,
            issuer_has_messenger_chat_admin_rights=is_admin,
        )
        return await self.__call_with_defaults(grpc_callable, request)

    async def unsubscribe_from_scope(
        self,
        scope_type: ScopeType,
        account_id: int,
        scope_id: int,
        chat_id: int,
        is_admin: bool,
    ):
        match scope_type:
            case ScopeType.ORGANIZATION:
                return await self._unsubscribe_from(
                    account_id,
                    scope_id,
                    chat_id,
                    is_admin,
                    self._integration_service.UnsubscribeFromOrganization,
                )
            case ScopeType.THREAD:
                return await self._unsubscribe_from(
                    account_id,
                    scope_id,
                    chat_id,
                    is_admin,
                    self._integration_service.UnsubscribeFromThread,
                )
            case ScopeType.DEADLINE:
                return await self._unsubscribe_from(
                    account_id,
                    scope_id,
                    chat_id,
                    is_admin,
                    self._integration_service.UnsubscribeFromDeadline,
                )

    async def unsubscribe_from_all(self, account_id: int, chat_id: int, is_admin: bool):
        request = integration_pb2.UnsubscribeFromAllRequest(
            issuer_messenger_account_id=account_id,
            messenger_chat_id=chat_id,
            messenger=self._messenger,
            issuer_has_messenger_chat_admin_rights=is_admin,
        )
        return await self.__call_with_defaults(
            self._integration_service.UnsubscribeFromAll, request
        )

    async def register_chat(
        self,
        account_id: int,
        chat_id: int,
        chat_title: str,
        preferences: ChatPreferences,
        is_admin: bool,
    ):
        request = integration_pb2.RegisterChatRequest(
            bot_id=self._bot_id,
            issuer_messenger_account_id=account_id,
            messenger=self._messenger,
            messenger_chat_id=chat_id,
            chat_title=chat_title,
            language=preferences.language.value,
            time_zone=preferences.time_zone,
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
        preferences: ChatPreferenceUpdates,
    ):
        request = integration_pb2.UpdateChatInfoRequest(
            issuer_messenger_account_id=account_id,
            messenger=self._messenger,
            messenger_chat_id=chat_id,
            title=chat_title,
            issuer_has_messenger_chat_admin_rights=is_admin,
        )
        if preferences.language is not None:
            request.language = getattr(integration_pb2, preferences.language.name)
        if preferences.time_zone is not None:
            request.time_zone = preferences.time_zone
        return await self.__call_with_defaults(
            self._integration_service.UpdateChatInfo, request
        )
