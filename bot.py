import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp

from src.config import *

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.reply(text=HELP_COMMAND)


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply(text=START_COMMAND)


@dp.message(Command("cat"))
async def cat_command(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(API_CATS_URL) as response:
            if response.status == 200:
                data = await response.json()
                cat_link = data[0]["url"]
                await message.reply_photo(photo=cat_link)
            else:
                await message.reply(text=ERROR_TEXT)


@dp.message(
    lambda message: message.text
    and message.text.startswith("/")
    and message.text not in COMMANDS
)
async def unknown_command(message: types.Message):
    await message.reply(
        "Неизвестная команда. Введите /help для списка доступных команд."
    )


@dp.message()
async def send_echo(message: types.Message):
    if message.text:
        await message.answer(text=message.text * 2)
    else:
        await message.answer("Я могу ответить только на текстовые сообщения.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
