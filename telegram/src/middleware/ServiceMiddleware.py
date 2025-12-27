from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware

from telegram.src.bot import telegram_grpc_client
from telegram.src.services.ChatService import ChatService
from telegram.src.services.help_service import HelpService
from telegram.src.services.SubscriptionService import SubscriptionService
from telegram.src.services.VerificationService import VerificationService


class ServiceMiddleware(BaseMiddleware):
    def __init__(self):
        self.subscription_service = SubscriptionService(telegram_grpc_client)
        self.verification_service = VerificationService(telegram_grpc_client)
        self.chat_service = ChatService(telegram_grpc_client)
        self.help_service = HelpService()

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        data["subscription_service"] = self.subscription_service
        data["verification_service"] = self.verification_service
        data["chat_service"] = self.chat_service
        data["help_service"] = self.help_service
        return await handler(event, data)
