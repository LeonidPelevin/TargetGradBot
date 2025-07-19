from aiogram import Router
from aiogram.types import Message
from src.lexicon.lexicon import LEXICON_RU

router = Router()


@router.message()
async def do_nothing(message: Message):
    await message.reply(text=LEXICON_RU["unknown_command"])
