import asyncio

from aiogram import Bot, Dispatcher

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.handlers import user_handlers
from app.config import Config, load_config
from app.keyboards.set_menu import set_main_menu
from app.middlewares import DatabaseMiddleware


async def main():
    config: Config = load_config()
    engine = create_async_engine(url=config.db.url, echo=True)
    session = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher()
    dp.include_router(user_handlers.router)
    dp.update.middleware(DatabaseMiddleware(session=session))
    await set_main_menu(bot=bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
