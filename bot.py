import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from src.config import BOT_TOKEN, HELP_COMMAND, START_COMMAND

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.reply(text=HELP_COMMAND)


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply(text=START_COMMAND)


@dp.message(
    lambda message: message.text
    and message.text.startswith("/")
    and not Command.filter(message)
)
async def unknown_command(message: types.Message):
    await message.reply(
        "Неизвестная команда. Введите /help для списка доступных команд."
    )


@dp.message(lambda message: message.text and not message.text.startswith("/"))
async def echo(message: types.Message):
    await message.answer(text=message.text * 2)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
