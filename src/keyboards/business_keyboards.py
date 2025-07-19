from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_survey_keyboard(
    question_number: int,
    options: list[str],
    multiple_choice: bool = False,
    selected: list[str] = None,
):
    builder = InlineKeyboardBuilder()
    if selected is None:
        selected = []

    for index, option in enumerate(options):
        text = f"✅ {option}" if option in selected else option
        callback_data = f"q_{question_number}:{index}"
        builder.button(text=text, callback_data=callback_data)

    if multiple_choice:
        builder.button(text="➡️ Далее", callback_data=f"q_{question_number}:next")

    builder.adjust(1)
    return builder.as_markup()
