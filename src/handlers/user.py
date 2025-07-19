import aiohttp
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from src.lexicon.lexicon import LEXICON_RU
from src.config.config import Config, load_config

config: Config = load_config()
router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU["/start"])


@router.message(Command(commands="help"))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU["/help"])


@router.message(Command(commands="cat"))
async def cat_command(message: Message):
    async with aiohttp.ClientSession() as session:
        print(config.bot.cats_api_url)
        async with session.get(config.bot.cats_api_url) as response:
            if response.status == 200:
                data = await response.json()
                cat_link = data[0]["url"]
                await message.reply_photo(photo=cat_link)
            else:
                await message.reply(text=LEXICON_RU["cat_error"])
