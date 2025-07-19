import asyncio
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

import logging
from together import Together

from src.config.config import Config, load_config
from src.data.programs import PROGRAMS_DATA
from src.keyboards.business_keyboards import get_survey_keyboard
from src.lexicon.lexicon import LEXICON_RU

config: Config = load_config()
router = Router()
MAX_MESSAGE_LENGTH = 4096


class BusinessSurvey(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    q6 = State()
    q7 = State()
    q8 = State()
    q9 = State()
    q10 = State()


SURVEY_QUESTIONS = {
    1: {"text": "q1_text", "options": "q1_options", "next_state": BusinessSurvey.q2},
    2: {"text": "q2_text", "options": "q2_options", "next_state": BusinessSurvey.q3},
    3: {"text": "q3_text", "options": "q3_options", "next_state": BusinessSurvey.q4},
    4: {"text": "q4_text", "options": "q4_options", "next_state": BusinessSurvey.q5},
    5: {
        "text": "q5_text",
        "options": "q5_options",
        "next_state": BusinessSurvey.q6,
        "multiple": True,
        "limit": 3,
    },
    6: {"text": "q6_text", "options": "q6_options", "next_state": BusinessSurvey.q7},
    7: {"text": "q7_text", "options": "q7_options", "next_state": BusinessSurvey.q8},
    8: {"text": "q8_text", "options": "q8_options", "next_state": BusinessSurvey.q9},
    9: {"text": "q9_text", "options": "q9_options", "next_state": BusinessSurvey.q10},
    10: {
        "text": "q10_text",
        "options": "q10_options",
        "next_state": None,
        "multiple": True,
        "limit": 2,
    },
}


async def process_recommendation_request(
    message: Message, user_answers: str
) -> str | None:
    client = Together(api_key=config.bot.together_api_key.strip())
    prompt = LEXICON_RU["business_prompt"].format(
        user_answers=user_answers, programs_list=PROGRAMS_DATA
    )
    history = [
        {"role": "system", "content": "Ты — профессиональный карьерный консультант."},
        {"role": "user", "content": prompt},
    ]
    try:

        def sync_call():
            return client.chat.completions.create(
                model="meta-llama/Llama-3-8b-chat-hf", messages=history
            )

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, sync_call)
        answer = response.choices[0].message.content
        return answer
    except Exception as e:
        logging.error(f"Error in API call: {e}")
        await message.answer(LEXICON_RU["neuro_error"].format(e=e))
        return None


@router.message(Command(commands="go"))
async def start_survey(message: Message, state: FSMContext):
    await message.answer(
        text=LEXICON_RU["business_start"],
    )
    await message.answer(
        text=LEXICON_RU["q1_text"],
        reply_markup=get_survey_keyboard(1, LEXICON_RU["q1_options"]),
    )
    await state.set_state(BusinessSurvey.q1)
    await state.update_data(answers={})


async def process_survey_step(
    callback: CallbackQuery, state: FSMContext, question_num: int
):
    data = await state.get_data()
    answers = data.get("answers", {})
    question_info = SURVEY_QUESTIONS[question_num]
    options_list = LEXICON_RU[question_info["options"]]
    raw_action = callback.data.split(":", 1)[1]
    action = ""
    if raw_action != "next":
        try:
            action_index = int(raw_action)
            action = options_list[action_index]
        except (ValueError, IndexError):
            await callback.answer("Ошибка: неверные данные кнопки.", show_alert=True)
            return
    else:
        action = "next"
    proceed = False
    if question_info.get("multiple"):
        selected = answers.get(f"q{question_num}", [])
        if action == "next":
            if not selected:
                await callback.answer(
                    "Пожалуйста, выберите хотя бы один вариант.", show_alert=True
                )
            else:
                proceed = True
        else:
            if action in selected:
                selected.remove(action)
            else:
                if len(selected) < question_info["limit"]:
                    selected.append(action)
                else:
                    await callback.answer(
                        f"Можно выбрать не более {question_info['limit']} вариантов.",
                        show_alert=True,
                    )
                    return
            answers[f"q{question_num}"] = selected
            await state.update_data(answers=answers)
            await callback.message.edit_reply_markup(
                reply_markup=get_survey_keyboard(
                    question_num, options_list, True, selected
                )
            )
            await callback.answer()
    else:
        answers[f"q{question_num}"] = [action]
        await state.update_data(answers=answers)
        proceed = True
    if proceed:
        next_state = question_info["next_state"]
        if next_state:
            next_question_num = question_num + 1
            await callback.message.edit_text(
                text=LEXICON_RU[SURVEY_QUESTIONS[next_question_num]["text"]],
                reply_markup=get_survey_keyboard(
                    next_question_num,
                    LEXICON_RU[SURVEY_QUESTIONS[next_question_num]["options"]],
                    SURVEY_QUESTIONS[next_question_num].get("multiple", False),
                ),
            )
            await state.set_state(next_state)
        else:
            await callback.message.edit_text(LEXICON_RU["business_processing"])
            final_answers_text = ""
            for i in range(1, 11):
                q_text_key = SURVEY_QUESTIONS[i]["text"]
                q_text = LEXICON_RU[q_text_key]
                ans_list = answers.get(f"q{i}", ["Не отвечено"])
                ans_str = ", ".join(ans_list)
                final_answers_text += f"Вопрос: {q_text}\nОтвет: {ans_str}\n\n"
            recommendation = await process_recommendation_request(
                callback.message, final_answers_text
            )
            if recommendation:
                await callback.message.answer(recommendation)
            await state.clear()
    await callback.answer()


@router.callback_query(BusinessSurvey.q1, F.data.startswith("q_1:"))
async def handle_q1(callback: CallbackQuery, state: FSMContext):
    await process_survey_step(callback, state, 1)


@router.callback_query(BusinessSurvey.q2, F.data.startswith("q_2:"))
async def handle_q2(callback: CallbackQuery, state: FSMContext):
    await process_survey_step(callback, state, 2)


@router.callback_query(BusinessSurvey.q3, F.data.startswith("q_3:"))
async def handle_q3(callback: CallbackQuery, state: FSMContext):
    await process_survey_step(callback, state, 3)


@router.callback_query(BusinessSurvey.q4, F.data.startswith("q_4:"))
async def handle_q4(callback: CallbackQuery, state: FSMContext):
    await process_survey_step(callback, state, 4)


@router.callback_query(BusinessSurvey.q5, F.data.startswith("q_5:"))
async def handle_q5(callback: CallbackQuery, state: FSMContext):
    await process_survey_step(callback, state, 5)


@router.callback_query(BusinessSurvey.q6, F.data.startswith("q_6:"))
async def handle_q6(callback: CallbackQuery, state: FSMContext):
    await process_survey_step(callback, state, 6)


@router.callback_query(BusinessSurvey.q7, F.data.startswith("q_7:"))
async def handle_q7(callback: CallbackQuery, state: FSMContext):
    await process_survey_step(callback, state, 7)


@router.callback_query(BusinessSurvey.q8, F.data.startswith("q_8:"))
async def handle_q8(callback: CallbackQuery, state: FSMContext):
    await process_survey_step(callback, state, 8)


@router.callback_query(BusinessSurvey.q9, F.data.startswith("q_9:"))
async def handle_q9(callback: CallbackQuery, state: FSMContext):
    await process_survey_step(callback, state, 9)


@router.callback_query(BusinessSurvey.q10, F.data.startswith("q_10:"))
async def handle_q10(callback: CallbackQuery, state: FSMContext):
    await process_survey_step(callback, state, 10)
