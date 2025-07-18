with open("token.txt", "r") as file:
    BOT_TOKEN = file.readline()

HELP_COMMAND = """
Доступные команды:
/start - запустить бота
/help - узнать список всех команд
/cat - получить кота
"""

START_COMMAND = """
Привет, это бот-ассистент TargerGrade!
Доступные команды:
/start - запустить бота
/help - узнать список команд
"""

API_CATS_URL = "https://api.thecatapi.com/v1/images/search"
ERROR_TEXT = "Здесь должна была быть картинка с котиком :("

COMMANDS = ["/start", "/help", "/cat"]
