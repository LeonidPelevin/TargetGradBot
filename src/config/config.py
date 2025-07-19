from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    bot_token: str
    together_api_key: str
    cats_api_url: str


@dataclass
class LogSettings:
    level: str
    format: str


@dataclass
class BotMessages:
    bot_start_message: str
    bot_help_message: str
    bot_cat_error_message: str


@dataclass
class Config:
    bot: TgBot
    log: LogSettings
    bot_messages: BotMessages


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        bot=TgBot(
            bot_token=env("BOT_TOKEN"),
            together_api_key=env("TOGETHER_API_KEY"),
            cats_api_url="CATS_API_URL",
        ),
        log=LogSettings(level=env("LOG_LEVEL"), format=env("LOG_FORMAT")),
        bot_messages=BotMessages(
            bot_start_message=env("START_MESSAGE"),
            bot_help_message=env("HELP_MESSAGE"),
            bot_cat_error_message=env("CAT_ERROR_MESSAGE"),
        ),
    )
