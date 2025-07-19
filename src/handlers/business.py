from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.lexicon.lexicon import LEXICON_RU

# from src.config.config import Config, load_config
# config: Config = load_config()

router = Router()


@router.message(Command(commands="go"))
async def run_proforientation(message: Message):
    await message.answer(text=LEXICON_RU["not_implemented"])
