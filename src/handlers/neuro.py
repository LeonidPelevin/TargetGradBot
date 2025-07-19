import asyncio
from together import Together
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.config.config import Config, load_config

config: Config = load_config()
router = Router()

MAX_MESSAGE_LENGTH = 4096


class Dialogue(StatesGroup):
    active = State()


@router.message(Command("neuro"))
async def neuro_command(message: Message, state: FSMContext):
    await state.set_state(Dialogue.active)
    initial_history = [
        {"role": "system", "content": "You are a helpful conversational assistant."}
    ]
    await state.update_data(history=initial_history)
    await message.answer(
        "Вы вошли в режим диалога с нейросетью. Просто пишите ваши сообщения.\n\n"
        "Для выхода введите /exit"
    )


async def process_dialogue_request(message: Message, history: list):
    processing_message = await message.answer("🧠 Думаю...")
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
        error_message = f"Произошла ошибка: {e}"
        await message.answer(error_message)
        return None
    finally:
        await processing_message.delete()


@router.message(Dialogue.active)
async def handle_dialogue(message: Message, state: FSMContext):
    if message.text.lower() == "/exit":
        await state.clear()
        await message.answer("Вы вышли из режима диалога.")
        return
    elif message.text and message.text[0] == "/":
        await message.answer(
            "Вы ввели неподдерживаемую команду. Если вы хотите выйти из режима диалога, введите /exit. "
            "Или продолжайте общение, не начиная сообщение со слеша."
        )
        return
    data = await state.get_data()
    history = data.get("history", [])
    history.append({"role": "user", "content": message.text})
    ai_response = await process_dialogue_request(message, history)
    if ai_response:
        await message.answer(ai_response + "\n\nДля выхода введите /exit")
        history.append({"role": "assistant", "content": ai_response})
        await state.update_data(history=history)
