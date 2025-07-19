import asyncio
import logging

from aiogram import Bot, Dispatcher
from src.config.config import Config, load_config
from src.handlers import other, user, business, neuro


async def main():
    config: Config = load_config()

    level_mapping = logging.getLevelNamesMapping()
    logging.basicConfig(
        level=level_mapping.get(config.log.level.upper(), logging.INFO),
        format=config.log.format,
    )

    bot = Bot(token=config.bot.bot_token)
    dp = Dispatcher()

    dp.include_router(user.router)
    dp.include_router(business.router)
    dp.include_router(neuro.router)
    dp.include_router(other.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
