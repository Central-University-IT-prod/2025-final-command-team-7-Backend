import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from bot.database import load_sessionmaker
from bot.handlers import setup_routers
from bot.middlewares import DBMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


async def main():
    bot_token = os.environ.get("BOT_TOKEN") or ""
    postgres_dsn = os.environ.get("POSTGRES_DSN")

    if not bot_token:
        logging.error("Bot token is not set")
        return

    if not postgres_dsn:
        logging.error("PostgreSQL DSN is not set")
        return

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    sessionmaker = load_sessionmaker(postgres_dsn)

    dp.update.middleware(DBMiddleware(sessionmaker))

    setup_routers(dp)

    try:
        logging.info("Starting bot")
        await dp.start_polling(bot)
    finally:
        logging.info("Shutting down bot")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
