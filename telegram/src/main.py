import asyncio
import logging

from common.config.bot_config import config
from common.i18n import configure_i18n
from telegram.src.bot import bot, dp, telegram_grpc_client

# Initializes error handlers
from telegram.src.exceptions.handlers import *  # noqa: F403
from telegram.src.kafka_consumers import global_consumer, kafka_handlers_setup
from telegram.src.middleware.ServiceMiddleware import ServiceMiddleware
from telegram.src.routers.chat_router import chat_router
from telegram.src.routers.help_router import help_router
from telegram.src.routers.subscription_router import subscription_router
from telegram.src.routers.util_router import util_router
from telegram.src.routers.verification_router import verification_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%H:%M:%S %d-%m-%Y",
)


@dp.startup()
async def on_startup():
    kafka_handlers_setup()
    await telegram_grpc_client.start()
    await global_consumer.start()


@dp.shutdown()
async def on_shutdown():
    await telegram_grpc_client.close()
    await global_consumer.stop()


async def main() -> None:
    configure_i18n(config.fallback_language)

    dp.include_router(subscription_router)
    dp.include_router(verification_router)
    dp.include_router(chat_router)
    dp.include_router(help_router)
    dp.include_router(util_router)

    dp.message.middleware(ServiceMiddleware())
    dp.callback_query.middleware(ServiceMiddleware())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
