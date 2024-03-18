from environs import Env

from dataclasses import dataclass


@dataclass(frozen=True)
class TgBot:
    token: str

@dataclass(frozen=True)
class Config:
    tg_bot: TgBot
    db_url: str

def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env()
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN')
        ),
        db_url=env('DB_URL')
    )