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
class Config:
    bot: TgBot
    log: LogSettings


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        bot=TgBot(
            bot_token=env("BOT_TOKEN"),
            together_api_key=env("TOGETHER_API_KEY"),
            cats_api_url=env("CATS_API_URL"),
        ),
        log=LogSettings(level=env("LOG_LEVEL"), format=env("LOG_FORMAT")),
    )
