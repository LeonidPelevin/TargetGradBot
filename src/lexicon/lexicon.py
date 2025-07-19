START_MESSAGE = """
Привет, это бот-ассистент TargerGrade!
Доступные команды:
/go - запустить поиск программ
/help - узнать список дополнительных функций
"""

HELP_MESSAGE = """
Доступные команды:
/start - запустить бота
/help - узнать список всех команд
/go - запустить поиск программ обучения
/cat - получить кота
/neuro - войти в режим диалога с нейросетью
"""

CAT_ERROR_MESSAGE = "Здесь должна была быть картинка с котиком :("

UNKNOWN_COMMAND = """
Неизвестная команда. Для получания списка доступных команд введите /help
"""

NOT_IMPLEMENTED_MESSAGE = "В разработке.."

LEXICON_RU: dict[str, str] = {
    "/start": START_MESSAGE,
    "/help": HELP_MESSAGE,
    "cat_error": CAT_ERROR_MESSAGE,
    "unknown_command": UNKNOWN_COMMAND,
    "not_implemented": NOT_IMPLEMENTED_MESSAGE,
}
