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

class NeuroState(StatesGroup):
    waiting_for_query = State()

async def process_neuro_request(
    message: types.Message, text: str, max_retries: int = 2
):
    for attempt in range(max_retries + 1):
        processing_message = await message.reply(
            "Processing your request... Note: Responses are limited to 4096 characters."
        )
        client = Together(api_key=API_KEY_TOGETHER.strip())
        try:

            def sync_call():
                return client.chat.completions.create(
                    model="meta-llama/Llama-Vision-Free",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant. Responses are limited to 4096 characters.",
                        },
                        {"role": "user", "content": text},
                    ],
                )

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, sync_call)
            answer = response.choices[0].message.content
            if len(answer) > MAX_MESSAGE_LENGTH:
                answer = answer[: MAX_MESSAGE_LENGTH - 3] + "..."
            await message.reply(answer)
            break
        except Exception as e:
            if (
                "429" in str(e)
                and "rate limit" in str(e).lower()
                and attempt < max_retries
            ):
                await message.reply("Достигнут лимит запросов. Повторная попытка...")
                await asyncio.sleep(2)
            else:
                error_msg = (
                    "Извините, достигнут лимит запросов. Попробуйте позже или свяжитесь с Together AI."
                    if "429" in str(e)
                    else f"Ошибка: {str(e)}"
                )
                await message.reply(error_msg)
        finally:
            await processing_message.delete()


@dp.message(Command("neuro"))
async def neuro_command(message: types.Message, state: FSMContext):
    text = message.text[len("/neuro"):].strip()
    
    if text:
        await process_neuro_request(message, text)
    else:
        await message.reply("Введите ваш запрос для нейросети или /exit для выхода.")
        await state.set_state(NeuroState.waiting_for_query)

@dp.message(NeuroState.waiting_for_query)
async def process_query_in_state(message: types.Message, state: FSMContext):
    if message.text.lower() == "/exit":
        await message.reply("Выход выполнен. Вы больше не в режиме диалога.")
        await state.clear()
        return

    await process_neuro_request(message, message.text)
    
    await state.clear()


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


# @dp.message(Command("neuro"))
# async def deepseek_command(message: types.Message):
#     processing_message = await message.reply(
#         "Processing your request... Note: Responses are limited to 4096 characters."
#     )

#     text = message.text[len("/deepseek") :].strip()
#     if not text:
#         await message.reply(
#             "Пожалуйста, укажите запрос после /deepseek, например: /deepseek What is the weather like?"
#         )
#         await processing_message.delete()
#         return
#     client = Together(api_key=API_KEY_TOGETHER.strip())
#     try:

#         def sync_call():
#             return client.chat.completions.create(
#                 model="meta-llama/Llama-Vision-Free",
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": "You are a helpful assistant. Responses are limited to 4096 characters.",
#                     },
#                     {"role": "user", "content": text},
#                 ],
#             )

#         loop = asyncio.get_event_loop()
#         response = await loop.run_in_executor(None, sync_call)
#         answer = response.choices[0].message.content
#         if len(answer) > MAX_MESSAGE_LENGTH:
#             answer = answer[: MAX_MESSAGE_LENGTH - 3] + "..."
#         await message.reply(answer)
#     except Exception as e:
#         await message.reply(f"Ошибка при обработке запроса: {str(e)}")
#     finally:
#         pass



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
