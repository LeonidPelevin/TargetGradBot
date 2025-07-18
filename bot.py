import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from together import Together

from src.config import *

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


class Dialogue(StatesGroup):
    active = State()


async def process_dialogue_request(message: types.Message, history: list):
    processing_message = await message.answer("🧠 Думаю...")
    client = Together(api_key=API_KEY_TOGETHER.strip())
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


@dp.message(Command("neuro"))
async def neuro_command(message: types.Message, state: FSMContext):
    await state.set_state(Dialogue.active)
    initial_history = [
        {"role": "system", "content": "You are a helpful conversational assistant."}
    ]
    await state.update_data(history=initial_history)
    await message.answer(
        "Вы вошли в режим диалога с нейросетью. Просто пишите ваши сообщения.\n\n"
        "Для выхода введите /exit"
    )


@dp.message(Dialogue.active)
async def handle_dialogue(message: types.Message, state: FSMContext):
    if message.text.lower() == "/exit":
        await state.clear()
        await message.answer("Вы вышли из режима диалога. История очищена.")
        return
    data = await state.get_data()
    history = data.get("history", [])

    history.append({"role": "user", "content": message.text})

    ai_response = await process_dialogue_request(message, history)

    if ai_response:
        await message.answer(ai_response)
        history.append({"role": "assistant", "content": ai_response})
        await state.update_data(history=history)


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
