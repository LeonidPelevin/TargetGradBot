from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY_TOGETHER = os.getenv("TOGETHER_API_KEY")

HELP_COMMAND = """
Доступные команды:
/start - запустить бота
/help - узнать список всех команд
/go - запустить поиск программ обучения
/cat - получить кота
/neuro - войти в режим диалога с нейросетью
"""

START_COMMAND = """
Привет, это бот-ассистент TargerGrade!
Доступные команды:
/go - запустить поиск программ
/help - узнать список дополнительных функций
"""

API_CATS_URL = "https://api.thecatapi.com/v1/images/search"
ERROR_TEXT = "Здесь должна была быть картинка с котиком :("

COMMANDS = ["/start", "/help", "/cat", "/go", "/neuro"]
MAX_MESSAGE_LENGTH = 4096
