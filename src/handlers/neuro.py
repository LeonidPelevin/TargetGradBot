import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from together import Together

from src.config.config import Config, load_config
from src.lexicon.lexicon import LEXICON_RU

config: Config = load_config()
router = Router()
MAX_MESSAGE_LENGTH = 4096


class Dialogue(StatesGroup):
    active = State()


async def process_dialogue_request(message: Message, history: list) -> str | None:
    processing_message = await message.answer(LEXICON_RU["neuro_thinking"])
    client = Together(api_key=config.bot.together_api_key.strip())
    try:

        def sync_call():
            return client.chat.completions.create(
                model="meta-llama/Llama-Vision-Free", messages=history
            )

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, sync_call)
        answer = response.choices[0].message.content

        if len(answer) > MAX_MESSAGE_LENGTH:
            answer = answer[: MAX_MESSAGE_LENGTH - 3] + "..."
        return answer

    except Exception as e:
        error_message = LEXICON_RU["neuro_error"].format(e=e)
        await message.answer(error_message)
        return None
    finally:
        await processing_message.delete()


@router.message(Command("neuro"))
async def neuro_command(message: Message, state: FSMContext):
    await state.set_state(Dialogue.active)
    initial_history = [
        {"role": "system", "content": "You are a helpful conversational assistant."}
    ]
    await state.update_data(history=initial_history)
    await message.answer(LEXICON_RU["neuro_start"])


@router.message(Dialogue.active, F.text)
async def handle_dialogue(message: Message, state: FSMContext):
    if message.text.lower() == "/exit":
        await state.clear()
        await message.answer(LEXICON_RU["neuro_exit"])
        return

    if message.text.startswith("/"):
        await message.answer(LEXICON_RU["neuro_unsupported_command"])
        return

    data = await state.get_data()
    history = data.get("history", [])

    history.append({"role": "user", "content": message.text})

    ai_response = await process_dialogue_request(message, history)

    if ai_response:
        await message.answer(ai_response + LEXICON_RU["neuro_response_suffix"])
        history.append({"role": "assistant", "content": ai_response})
        await state.update_data(history=history)
