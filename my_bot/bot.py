import asyncio
import os

from aiogram import (
    Bot,
    Dispatcher
)

from handlers import router

from menu import set_bot_commands


# ============================================================
# BOT TOKEN
# ============================================================

TOKEN = os.getenv(
    "BOT_TOKEN"
)


# ============================================================
# MAIN
# ============================================================

async def main():

    # Check that the Telegram token exists.
    if TOKEN is None:

        raise ValueError(
            "BOT_TOKEN environment variable is not set."
        )


    # Create bot.
    bot = Bot(
        token=TOKEN
    )


    # Create dispatcher.
    dp = Dispatcher()


    # Register all handlers from handlers.py.
    dp.include_router(
        router
    )


    # Create Telegram command menu.
    await set_bot_commands(
        bot
    )


    print(
        "GaruBB bot is running..."
    )


    # Start listening for Telegram messages.
    await dp.start_polling(
        bot
    )


# ============================================================
# RUN BOT
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )