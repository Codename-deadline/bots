from typing import cast

import grpc
from grpc import StatusCode
from grpc.aio import Channel

from common.grpc.generated import integration_pb2
from common.grpc.generated import integration_pb2_grpc
from common.logic.enums import Messenger, Language
from common.logic.grpc.GrpcResponse import GrpcResponse
from common.logic.utils import get_logger_from_filepath
from common.config.bot_config import config


class GrpcClient:
    __logger = get_logger_from_filepath(__file__)
    __channel: Channel

    integration_service: integration_pb2_grpc.IntegrationServiceStub

    def __init__(
        self,
        target: str,
        messenger: Messenger,
        bot_id: int,
        is_secure: bool = False,
        credentials=None,
        timeout: float = 5.0,
    ):
        self.__target: str = target
        self.__is_secure: bool = is_secure
        self.__credentials = credentials
        self.__timeout: float = timeout
        self.__messenger: integration_pb2.ProtoMessenger = cast(
            integration_pb2.ProtoMessenger, messenger
        )
        self.__bot_id: int = bot_id

    async def start(self):
        """Open channel and instantiate stubs. Call at app startup."""
        if self.__is_secure:
            assert self.__credentials is not None
            self.__channel = grpc.aio.secure_channel(self.__target, self.__credentials)
        else:
            self.__channel = grpc.aio.insecure_channel(self.__target)

        self.integration_service = integration_pb2_grpc.IntegrationServiceStub(
            self.__channel
        )

        # TODO: Add health check

    async def close(self):
        await self.__channel.close()

    # rpc_error_callback: Callable[[StatusCode, str], Awaitable[None]] = lambda x, y: None
    async def __call_with_defaults(
        self, method, request, timeout=None, metadata=None
    ) -> GrpcResponse:
        """Generic wrapper that applies default timeout & metadata."""
        if timeout is None:
            timeout = self.__timeout
        try:
            res = cast(
                integration_pb2.GeneralResponse,
                await method(request, timeout=timeout, metadata=metadata),
            )
            return GrpcResponse(
                is_error=False,
                key=res.key,
                language=Language(tuple(e.value for e in Language)[res.locale]),
            )
        except grpc.RpcError as rpc_error:
            e = cast(grpc.aio.AioRpcError, rpc_error)
            self.__logger.error(
                f"Grpc error occurred. Status code: {e.code()}. Details: {e.details()}"
            )

            return GrpcResponse(
                is_error=True,
                key=e.details()
                if e.code() != StatusCode.UNAVAILABLE
                else "errors.server_unavailable",
                language=Language(
                    e.trailing_metadata().get("locale") or config.fallback_language.name
                ),
            )

    async def link_messenger_account(self, request_id: str, is_accepted: bool):
        request = integration_pb2.LinkMessengerAccountRequest(
            request_id=request_id, is_accepted=is_accepted
        )
        return await self.__call_with_defaults(
            self.integration_service.LinkMessengerAccount, request
        )

    async def __subscribe_to(
        self, user_id: int, target_id: int, chat_id: int, grpc_callable
    ):
        request = integration_pb2.SubscribeToRequest(
            issuer_account_id=user_id,
            target_id=target_id,
            messenger_chat_id=chat_id,
            messenger=self.__messenger,
        )
        return await self.__call_with_defaults(grpc_callable, request)

    async def subscribe_to_organization(
        self, user_id: int, target_id: int, chat_id: int
    ):
        return await self.__subscribe_to(
            user_id,
            target_id,
            chat_id,
            self.integration_service.SubscribeToOrganization,
        )

    async def subscribe_to_thread(self, user_id: int, target_id: int, chat_id: int):
        return await self.__subscribe_to(
            user_id, target_id, chat_id, self.integration_service.SubscribeToThread
        )

    async def subscribe_to_deadline(self, user_id: int, target_id: int, chat_id: int):
        return await self.__subscribe_to(
            user_id, target_id, chat_id, self.integration_service.SubscribeToDeadline
        )

    async def __unsubscribe_from(
        self, user_id: int, target_id: int, chat_id: int, grpc_callable
    ):
        request = integration_pb2.UnsubscribeFromRequest(
            issuer_account_id=user_id,
            target_id=target_id,
            messenger_chat_id=chat_id,
            messenger=self.__messenger,
        )
        return await self.__call_with_defaults(grpc_callable, request)

    async def unsubscribe_from_organization(
        self, user_id: int, target_id: int, chat_id: int
    ):
        return await self.__unsubscribe_from(
            user_id,
            target_id,
            chat_id,
            self.integration_service.SubscribeToOrganization,
        )

    async def unsubscribe_from_thread(self, user_id: int, target_id: int, chat_id: int):
        return await self.__unsubscribe_from(
            user_id, target_id, chat_id, self.integration_service.SubscribeToThread
        )

    async def unsubscribe_from_deadline(
        self, user_id: int, target_id: int, chat_id: int
    ):
        return await self.__unsubscribe_from(
            user_id, target_id, chat_id, self.integration_service.SubscribeToDeadline
        )

    async def unsubscribe_from_all(self, user_id: int, chat_id: int):
        request = integration_pb2.UnsubscribeFromAllRequest(
            issuer_account_id=user_id,
            messenger_chat_id=chat_id,
            messenger=self.__messenger,
        )
        return await self.__call_with_defaults(
            self.integration_service.UnsubscribeFromAll, request
        )

    async def register_chat(
        self, issuer_id: int, chat_id: int, chat_title: str, language: Language
    ):
        request = integration_pb2.RegisterChatRequest(
            bot_id=self.__bot_id,
            issuer_account_id=issuer_id,
            messenger=self.__messenger,
            messenger_chat_id=chat_id,
            chat_title=chat_title,
            language=language,
        )
        return await self.__call_with_defaults(
            self.integration_service.RegisterChat, request
        )

    async def deregister_chat(self, chat_id: int):
        return await self.__call_with_defaults(
            self.integration_service.DeregisterChat,
            integration_pb2.DeregisterChatRequest(
                messenger_chat_id=chat_id, messenger=self.__messenger
            ),
        )

    async def update_chat_info(
        self, issuer_id: int, chat_id: int, chat_title: str, language: Language | None
    ):
        request = integration_pb2.UpdateChatInfoRequest(
            issuer_account_id=issuer_id,
            messenger=self.__messenger,
            messenger_chat_id=chat_id,
            language=language,
            title=chat_title,
        )
        return await self.__call_with_defaults(
            self.integration_service.UpdateChatInfo, request
        )
