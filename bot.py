import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, DB_CONFIG
from handlers import start, link_handler, instagram_content, youtube_content
from utils import db

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Routers
dp.include_router(start.router)
dp.include_router(link_handler.router)
dp.include_router(instagram_content.router)
dp.include_router(youtube_content.router)


async def on_startup():
    logging.info("Initializing DB pool...")
    await db.init_pool(DB_CONFIG)
    await db.ensure_schema()
    logging.info("DB ready.")

async def on_shutdown():
    logging.info("Closing DB pool...")
    await db.close_pool()
    logging.info("DB closed.")

dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
