import asyncio
import logging
import os
import sys

import django


def setup_django() -> None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "micron.settings")
    django.setup()


async def main() -> None:
    from aiogram import Dispatcher

    from tg_bot.bot import bot
    from tg_bot.handlers import router

    logging.basicConfig(level=logging.INFO)

    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    setup_django()
    asyncio.run(main())

