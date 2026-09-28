from aiogram import Bot

from aiogram.types import BotCommand


# ============================================================
# TELEGRAM COMMAND MENU
# ============================================================

async def set_bot_commands(
    bot: Bot
):

    commands = [

        BotCommand(
            command="start",
            description="Show your GaruBB partner"
        ),

        BotCommand(
            command="tasks",
            description="View tasks and completion status"
        ),

        BotCommand(
            command="complete",
            description="Complete a task and earn points"
        ),

        BotCommand(
            command="undo",
            description="Undo a completed task"
        ),

        BotCommand(
            command="score",
            description="View your score and leaderboard position"
        ),

        BotCommand(
            command="leaderboards",
            description="View the GaruBB leaderboard"
        ),

        BotCommand(
            command="help",
            description="Show commands and instructions"
        )
    ]


    await bot.set_my_commands(
        commands
    )