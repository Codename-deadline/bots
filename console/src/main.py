import asyncio
import contextlib
import logging

from common.config.bot_config import config
from common.infrastructure.i18n.translator import I18nTranslator
from common.infrastructure.logging import configure_logging
from console.src.adapter import ConsoleMessengerAdapter
from console.src.kafka_consumer import build_console_consumer

logger = logging.getLogger(__name__)


async def main() -> None:
    configure_logging()

    translator = I18nTranslator(config.fallback_language)
    messenger = ConsoleMessengerAdapter(translator)
    consumer = build_console_consumer(config.kafka, messenger, translator)

    await consumer.start()
    logger.info("Console Kafka consumer started")

    try:
        await asyncio.Event().wait()
    finally:
        await consumer.stop()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
