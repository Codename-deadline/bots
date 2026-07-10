from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware


class ServiceMiddleware(BaseMiddleware):
    def __init__(self, **dependencies):
        self.dependencies = dependencies

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        data.update(self.dependencies)
        return await handler(event, data)
