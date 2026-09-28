from aiogram import Router

from aiogram.filters import (
    Command,
    CommandStart
)

from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

from aiogram.fsm.context import FSMContext

from aiogram.fsm.state import (
    State,
    StatesGroup
)

from database import (
    Database,
    TASKS
)


# ============================================================
# ROUTER
# ============================================================

router = Router()


# ============================================================
# DATABASE
# ============================================================

db = Database("bot.db")


# ============================================================
# FSM STATES
# ============================================================

class CompleteTaskState(StatesGroup):

    choosing_task = State()

    confirming_task = State()


class UndoTaskState(StatesGroup):

    choosing_task = State()

    confirming_task = State()


# ============================================================
# TASK KEYBOARD
# ============================================================

def task_keyboard(task_names):

    keyboard = []


    for task_name in task_names:

        keyboard.append(
            [
                KeyboardButton(
                    text=task_name
                )
            ]
        )


    keyboard.append(
        [
            KeyboardButton(
                text="Cancel"
            )
        ]
    )


    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


# ============================================================
# YES / NO KEYBOARD
# ============================================================

def confirmation_keyboard():

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Yes"
                ),

                KeyboardButton(
                    text="No"
                )
            ]
        ],

        resize_keyboard=True
    )


# ============================================================
# /start
# ============================================================

@router.message(CommandStart())
async def start_command(
    message: Message
):

    username = message.from_user.username


    if username is None:

        await message.answer(
            "You need to set a Telegram username before using this bot."
        )

        return


    username = username.lower()


    pair = db.get_person(
        username
    )


    if pair is None:

        await message.answer(
            "I couldn't find you in the GaruBB database."
        )

        return


    # --------------------------------------------------------
    # User is the person side
    # --------------------------------------------------------

    if pair["person_tele_handle"] == username:

        user_name = pair[
            "person_name"
        ]


        garubb_name = pair[
            "partner_name"
        ]


        garubb_handle = pair[
            "partner_tele_handle"
        ]


        garubb_statement = pair[
            "partner_statement"
        ]


    # --------------------------------------------------------
    # User is the partner side
    # --------------------------------------------------------

    else:

        user_name = pair[
            "partner_name"
        ]


        garubb_name = pair[
            "person_name"
        ]


        garubb_handle = pair[
            "person_tele_handle"
        ]


        garubb_statement = pair[
            "person_statement"
        ]


    # Add @ for display.
    if garubb_handle:

        garubb_handle = (
            f"@{garubb_handle}"
        )

    else:

        garubb_handle = (
            "No Telegram handle"
        )


    if not garubb_statement:

        garubb_statement = "_"


    await message.answer(
        f"Hi {user_name}, your GaruBB is...\n\n"
        f"{garubb_name} {garubb_handle}!!!\n\n"
        f"Here is what your GaruBB wants to say to you:\n"
        f"{garubb_statement}"
    )


# ============================================================
# /help
# ============================================================

@router.message(Command("help"))
async def help_command(
    message: Message
):

    help_text = (
        "🤖 GaruBB Bot Commands\n\n"

        "/start\n"
        "Shows who your GaruBB is, their Telegram handle, "
        "and their statement to you.\n\n"

        "/tasks\n"
        "Shows all available tasks, their point values, "
        "and whether your pair has completed them.\n\n"

        "/complete\n"
        "Complete a task and earn points.\n"
        "1. Send /complete\n"
        "2. Choose an unfinished task\n"
        "3. Press Yes to confirm\n"
        "4. Your pair earns the corresponding points.\n\n"

        "/undo\n"
        "Undo a completed task.\n"
        "1. Send /undo\n"
        "2. Choose a completed task\n"
        "3. Press Yes to confirm\n"
        "4. The task is removed and its points are deducted.\n\n"

        "/score\n"
        "Shows your pair's current score and leaderboard position.\n\n"

        "/leaderboards\n"
        "Shows the top 10 GaruBB pairs and your pair's current "
        "position on the leaderboard.\n\n"

        "/help\n"
        "Shows this list of commands."
    )


    await message.answer(
        help_text
    )


# ============================================================
# /tasks
# ============================================================

@router.message(Command("tasks"))
async def tasks_command(
    message: Message
):

    username = message.from_user.username


    if username is None:

        await message.answer(
            "You need to set a Telegram username before using this bot."
        )

        return


    pair = db.get_person(
        username
    )


    if pair is None:

        await message.answer(
            "I couldn't find you in the GaruBB database."
        )

        return


    completed_tasks = db.get_completed_tasks(
        username
    )


    completed_tasks = set(
        completed_tasks
    )


    task_text = (
        "Here are the tasks!!! 🎯\n\n"
    )


    for task_name, task_info in TASKS.items():

        description = task_info[
            "description"
        ]


        points = task_info[
            "points"
        ]


        if task_name in completed_tasks:

            status = "✅ completed"

        else:

            status = "❌ not completed"


        task_text += (
            f"{task_name} - "
            f"{description} - "
            f"{points} points "
            f"({status})\n\n"
        )


    await message.answer(
        task_text
    )


# ============================================================
# /score
# ============================================================

@router.message(Command("score"))
async def score_command(
    message: Message
):

    username = message.from_user.username


    if username is None:

        await message.answer(
            "You need to set a Telegram username before using this bot."
        )

        return


    pair = db.get_person(
        username
    )


    if pair is None:

        await message.answer(
            "I couldn't find you in the GaruBB database."
        )

        return


    score = pair[
        "score"
    ]


    rank = db.get_pair_rank(
        username
    )


    total_pairs = db.get_pair_count()


    await message.answer(
        f"🏆 Your GaruBB pair currently has {score} points!\n\n"
        f"Your position: #{rank} out of {total_pairs} pairs."
    )


# ============================================================
# /leaderboards
# ============================================================

@router.message(Command("leaderboards"))
async def leaderboards_command(
    message: Message
):

    username = message.from_user.username


    leaderboard = db.get_leaderboard()


    if not leaderboard:

        await message.answer(
            "There are no pairs on the leaderboard yet."
        )

        return


    leaderboard_text = (
        "🏆 GaruBB Leaderboard 🏆\n\n"
    )


    # Used to correctly display ties.
    previous_score = None

    displayed_rank = 0


    for index, pair in enumerate(
        leaderboard,
        start=1
    ):

        # If score changes, update rank.
        #
        # Example:
        #
        # 1. 50
        # 2. 40
        # 2. 40
        # 4. 30
        if pair["score"] != previous_score:

            displayed_rank = index


        leaderboard_text += (
            f"{displayed_rank}. "
            f"{pair['person_name']} & "
            f"{pair['partner_name']} — "
            f"{pair['score']} points\n"
        )


        previous_score = pair[
            "score"
        ]


    # --------------------------------------------------------
    # Show the user's own position
    # --------------------------------------------------------

    if username is not None:

        user_pair = db.get_person(
            username
        )


        if user_pair is not None:

            rank = db.get_pair_rank(
                username
            )


            total_pairs = db.get_pair_count()


            score = user_pair[
                "score"
            ]


            leaderboard_text += (
                "\n"
                "--------------------\n\n"

                f"Your pair: "
                f"{user_pair['person_name']} & "
                f"{user_pair['partner_name']}\n"

                f"Score: {score} points\n"

                f"Position: #{rank} "
                f"out of {total_pairs}"
            )


    await message.answer(
        leaderboard_text
    )


# ============================================================
# /complete
# ============================================================

@router.message(Command("complete"))
async def complete_command(
    message: Message,
    state: FSMContext
):

    username = message.from_user.username


    if username is None:

        await message.answer(
            "You need to set a Telegram username before using this bot."
        )

        return


    pair = db.get_person(
        username
    )


    if pair is None:

        await message.answer(
            "I couldn't find you in the GaruBB database."
        )

        return


    completed_tasks = set(
        db.get_completed_tasks(
            username
        )
    )


    # Only tasks not already completed.
    available_tasks = [
        task_name

        for task_name in TASKS

        if task_name not in completed_tasks
    ]


    if not available_tasks:

        await message.answer(
            "You have completed all available tasks! 🎉",
            reply_markup=ReplyKeyboardRemove()
        )

        return


    await state.set_state(
        CompleteTaskState.choosing_task
    )


    await message.answer(
        "What task have you completed?",
        reply_markup=task_keyboard(
            available_tasks
        )
    )


# ============================================================
# COMPLETE - SELECT TASK
# ============================================================

@router.message(
    CompleteTaskState.choosing_task
)
async def choose_complete_task(
    message: Message,
    state: FSMContext
):

    selected_task = message.text


    if selected_task is None:
        return


    # Cancel task completion.
    if selected_task.strip().lower() == "cancel":

        await state.clear()


        await message.answer(
            "Task completion cancelled.",
            reply_markup=ReplyKeyboardRemove()
        )

        return


    selected_task = (
        selected_task
        .strip()
        .lower()
    )


    username = message.from_user.username


    if username is None:

        await state.clear()

        return


    # Recheck completed tasks in case database changed.
    completed_tasks = set(
        db.get_completed_tasks(
            username
        )
    )


    available_tasks = [
        task_name

        for task_name in TASKS

        if task_name not in completed_tasks
    ]


    if selected_task not in available_tasks:

        await message.answer(
            "Please choose one of the available tasks using the buttons."
        )

        return


    # Remember which task was selected.
    await state.update_data(
        selected_task=selected_task
    )


    await state.set_state(
        CompleteTaskState.confirming_task
    )


    await message.answer(
        f"Are you sure you finished {selected_task}?",
        reply_markup=confirmation_keyboard()
    )


# ============================================================
# COMPLETE - CONFIRM
# ============================================================

@router.message(
    CompleteTaskState.confirming_task
)
async def confirm_complete_task(
    message: Message,
    state: FSMContext
):

    answer = message.text


    if answer is None:
        return


    answer = (
        answer
        .strip()
        .lower()
    )


    # User selected No.
    if answer == "no":

        await state.clear()


        await message.answer(
            "Task was not marked as completed.",
            reply_markup=ReplyKeyboardRemove()
        )

        return


    if answer != "yes":

        await message.answer(
            "Please choose Yes or No."
        )

        return


    data = await state.get_data()


    selected_task = data[
        "selected_task"
    ]


    username = message.from_user.username


    if username is None:

        await state.clear()

        return


    success = db.complete_task(
        username,
        selected_task
    )


    await state.clear()


    if success:

        points = TASKS[
            selected_task
        ]["points"]


        await message.answer(
            f"✅ {selected_task} completed!\n"
            f"You earned {points} points! 🎉",
            reply_markup=ReplyKeyboardRemove()
        )


    else:

        await message.answer(
            "That task has already been completed.",
            reply_markup=ReplyKeyboardRemove()
        )


# ============================================================
# /undo
# ============================================================

@router.message(Command("undo"))
async def undo_command(
    message: Message,
    state: FSMContext
):

    username = message.from_user.username


    if username is None:

        await message.answer(
            "You need to set a Telegram username before using this bot."
        )

        return


    pair = db.get_person(
        username
    )


    if pair is None:

        await message.answer(
            "I couldn't find you in the GaruBB database."
        )

        return


    completed_tasks = db.get_completed_tasks(
        username
    )


    if not completed_tasks:

        await message.answer(
            "You haven't completed any tasks yet.",
            reply_markup=ReplyKeyboardRemove()
        )

        return


    await state.set_state(
        UndoTaskState.choosing_task
    )


    await message.answer(
        "What task would you like to undo?",
        reply_markup=task_keyboard(
            completed_tasks
        )
    )


# ============================================================
# UNDO - SELECT TASK
# ============================================================

@router.message(
    UndoTaskState.choosing_task
)
async def choose_undo_task(
    message: Message,
    state: FSMContext
):

    selected_task = message.text


    if selected_task is None:
        return


    # Cancel.
    if selected_task.strip().lower() == "cancel":

        await state.clear()


        await message.answer(
            "Undo cancelled.",
            reply_markup=ReplyKeyboardRemove()
        )

        return


    selected_task = (
        selected_task
        .strip()
        .lower()
    )


    username = message.from_user.username


    if username is None:

        await state.clear()

        return


    completed_tasks = db.get_completed_tasks(
        username
    )


    if selected_task not in completed_tasks:

        await message.answer(
            "Please choose one of your completed tasks using the buttons."
        )

        return


    # Remember selected task.
    await state.update_data(
        selected_task=selected_task
    )


    await state.set_state(
        UndoTaskState.confirming_task
    )


    await message.answer(
        f"Are you sure you want to undo {selected_task} task?",
        reply_markup=confirmation_keyboard()
    )


# ============================================================
# UNDO - CONFIRM
# ============================================================

@router.message(
    UndoTaskState.confirming_task
)
async def confirm_undo_task(
    message: Message,
    state: FSMContext
):

    answer = message.text


    if answer is None:
        return


    answer = (
        answer
        .strip()
        .lower()
    )


    # User selected No.
    if answer == "no":

        await state.clear()


        await message.answer(
            "Task was not undone.",
            reply_markup=ReplyKeyboardRemove()
        )

        return


    if answer != "yes":

        await message.answer(
            "Please choose Yes or No."
        )

        return


    data = await state.get_data()


    selected_task = data[
        "selected_task"
    ]


    username = message.from_user.username


    if username is None:

        await state.clear()

        return


    success = db.undo_task(
        username,
        selected_task
    )


    await state.clear()


    if success:

        points = TASKS[
            selected_task
        ]["points"]


        await message.answer(
            f"↩️ {selected_task} was undone.\n"
            f"{points} points were deducted.",
            reply_markup=ReplyKeyboardRemove()
        )


    else:

        await message.answer(
            "That task was not completed, so it could not be undone.",
            reply_markup=ReplyKeyboardRemove()
        )