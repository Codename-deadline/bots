import asyncio

from common.infrastructure.logging import configure_logging
from telegram.src.bot import (
    bot,
    chat_service,
    dp,
    global_consumer,
    help_service,
    integration_gateway,
    subscription_service,
    translator,
    verification_service,
)

# Initializes error handlers
from telegram.src.exceptions.handlers import *  # noqa: F403
from telegram.src.middleware.ServiceMiddleware import ServiceMiddleware
from telegram.src.routers.chat_router import chat_router
from telegram.src.routers.help_router import help_router
from telegram.src.routers.subscription_router import subscription_router
from telegram.src.routers.util_router import util_router
from telegram.src.routers.verification_router import verification_router


@dp.startup()
async def on_startup():
    await integration_gateway.start()
    await global_consumer.start()


@dp.shutdown()
async def on_shutdown():
    await integration_gateway.close()
    await global_consumer.stop()


async def main() -> None:
    configure_logging()

    dp.include_routers(
        subscription_router, verification_router, chat_router, help_router, util_router
    )

    middleware = ServiceMiddleware(
        chat_service=chat_service,
        subscription_service=subscription_service,
        verification_service=verification_service,
        help_service=help_service,
        translator=translator,
    )
    dp.message.middleware(middleware)
    dp.callback_query.middleware(middleware)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
