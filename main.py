from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
import asyncio

TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

dp.include_router(router)


async def set_commands():
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Show help"),
        BotCommand(command="profile", description="Show your username")
    ]

    await bot.set_my_commands(commands)


@router.message(CommandStart())
async def start_command(message: Message):
    username = message.from_user.username

    if username:
        await message.answer(
            f"Hello @{username}!\n\nUse the menu to choose a command."
        )
    else:
        await message.answer(
            "Hello!\n\nUse the menu to choose a command."
        )


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "/start - Start the bot\n"
        "/help - Show help\n"
        "/profile - Show your username"
    )


@router.message(Command("profile"))
async def profile_command(message: Message):
    username = message.from_user.username

    if username:
        await message.answer(f"Your username is @{username}")
    else:
        await message.answer("You don't have a Telegram username set.")


async def main():
    await set_commands()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
