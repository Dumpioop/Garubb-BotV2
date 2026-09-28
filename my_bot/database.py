import sqlite3
import pandas as pd


# ============================================================
# TASKS
# ============================================================

TASKS = {
    "movies": {
        "description": "watch a movie with your GaruBB",
        "points": 5
    },

    "tiktok": {
        "description": "film a TikTok with your GaruBB",
        "points": 10
    },

    "food review": {
        "description": "do a food review with your GaruBB",
        "points": 5
    },

    "photo": {
        "description": "take a photo with your GaruBB",
        "points": 5
    }
}


# ============================================================
# DATABASE CLASS
# ============================================================

class Database:

    def __init__(self, filename="bot.db"):

        # Connect to SQLite.
        # If the database file does not exist, it is created.
        self.conn = sqlite3.connect(filename)

        # Allows:
        # row["person_name"]
        #
        # instead of:
        # row[1]
        self.conn.row_factory = sqlite3.Row


        # Create the people table if it does not exist.
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS people (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                person_name TEXT NOT NULL,

                person_tele_handle TEXT UNIQUE,

                person_statement TEXT,

                partner_name TEXT,

                partner_tele_handle TEXT UNIQUE,

                partner_statement TEXT,

                task_completed TEXT NOT NULL DEFAULT '_',

                score INTEGER NOT NULL DEFAULT 0
            )
        """)

        self.conn.commit()


    # ========================================================
    # CLEAN NORMAL EXCEL CELL
    # ========================================================

    def _clean_cell(self, value):

        if pd.isna(value):
            return None

        return str(value).strip()


    # ========================================================
    # CLEAN TELEGRAM HANDLE
    # ========================================================

    def _clean_handle(self, value):

        if pd.isna(value):
            return None

        handle = str(value).strip()

        if handle == "":
            return None

        # @Titus123 -> titus123
        return handle.lstrip("@").lower()


    # ========================================================
    # IMPORT DATA FROM EXCEL
    # ========================================================

    def import_excel(self, filename):

        df = pd.read_excel(filename)


        required_columns = [
            "Person name",
            "Person tele handle",
            "Person statement",
            "Partner name",
            "Partner tele handle",
            "Partner statement"
        ]


        # Check for missing spreadsheet columns.
        missing_columns = []

        for column in required_columns:

            if column not in df.columns:
                missing_columns.append(column)


        if missing_columns:

            raise ValueError(
                f"Missing columns in Excel sheet: {missing_columns}"
            )


        # Read spreadsheet one row at a time.
        for _, row in df.iterrows():

            person_name = self._clean_cell(
                row["Person name"]
            )

            person_tele_handle = self._clean_handle(
                row["Person tele handle"]
            )

            person_statement = self._clean_cell(
                row["Person statement"]
            )

            partner_name = self._clean_cell(
                row["Partner name"]
            )

            partner_tele_handle = self._clean_handle(
                row["Partner tele handle"]
            )

            partner_statement = self._clean_cell(
                row["Partner statement"]
            )


            # Skip blank rows.
            if not person_name:
                continue


            # Insert new row.
            #
            # If person_tele_handle already exists,
            # update participant information.
            #
            # score and task_completed are deliberately
            # NOT changed when importing again.
            self.conn.execute(
                """
                INSERT INTO people (

                    person_name,
                    person_tele_handle,
                    person_statement,

                    partner_name,
                    partner_tele_handle,
                    partner_statement
                )

                VALUES (?, ?, ?, ?, ?, ?)

                ON CONFLICT(person_tele_handle)

                DO UPDATE SET

                    person_name =
                        excluded.person_name,

                    person_statement =
                        excluded.person_statement,

                    partner_name =
                        excluded.partner_name,

                    partner_tele_handle =
                        excluded.partner_tele_handle,

                    partner_statement =
                        excluded.partner_statement
                """,

                (
                    person_name,
                    person_tele_handle,
                    person_statement,

                    partner_name,
                    partner_tele_handle,
                    partner_statement
                )
            )


        self.conn.commit()


    # ========================================================
    # FIND PAIR USING TELEGRAM USERNAME
    # ========================================================

    def get_person(self, telegram_handle):

        if telegram_handle is None:
            return None


        telegram_handle = (
            telegram_handle
            .lstrip("@")
            .lower()
        )


        return self.conn.execute(
            """
            SELECT *
            FROM people

            WHERE person_tele_handle = ?

            OR partner_tele_handle = ?
            """,

            (
                telegram_handle,
                telegram_handle
            )

        ).fetchone()


    # ========================================================
    # GET ALL PAIRS
    # ========================================================

    def get_all_people(self):

        return self.conn.execute(
            """
            SELECT *
            FROM people
            ORDER BY id
            """
        ).fetchall()


    # ========================================================
    # GET NUMBER OF PAIRS
    # ========================================================

    def get_pair_count(self):

        return self.conn.execute(
            """
            SELECT COUNT(*)
            FROM people
            """
        ).fetchone()[0]


    # ========================================================
    # GET TOP 10 LEADERBOARD
    # ========================================================

    def get_leaderboard(self):

        return self.conn.execute(
            """
            SELECT *
            FROM people

            ORDER BY score DESC, id ASC

            LIMIT 10
            """
        ).fetchall()


    # ========================================================
    # GET PAIR RANK
    # ========================================================

    def get_pair_rank(self, telegram_handle):

        pair = self.get_person(
            telegram_handle
        )


        if pair is None:
            return None


        score = pair["score"]


        # Count how many pairs have a strictly higher score.
        higher_scores = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM people

            WHERE score > ?
            """,

            (score,)
        ).fetchone()[0]


        # Example:
        #
        # 3 pairs above you
        # means you are position 4.
        return higher_scores + 1


    # ========================================================
    # GET COMPLETED TASKS
    # ========================================================

    def get_completed_tasks(self, telegram_handle):

        pair = self.get_person(
            telegram_handle
        )


        if pair is None:
            return None


        current_tasks = pair[
            "task_completed"
        ]


        # "_" means no completed tasks.
        if current_tasks == "_":
            return []


        # "movies, tiktok"
        #
        # becomes:
        #
        # ["movies", "tiktok"]
        return [
            task.strip().lower()

            for task in current_tasks.split(",")

            if task.strip()
        ]


    # ========================================================
    # COMPLETE TASK
    # ========================================================

    def complete_task(
        self,
        telegram_handle,
        task_name
    ):

        if telegram_handle is None:
            return False


        telegram_handle = (
            telegram_handle
            .lstrip("@")
            .lower()
        )


        task_name = (
            task_name
            .strip()
            .lower()
        )


        # Check that task exists.
        if task_name not in TASKS:

            raise ValueError(
                f"Unknown task: {task_name}"
            )


        # Find the pair.
        pair = self.get_person(
            telegram_handle
        )


        if pair is None:

            raise ValueError(
                f"User @{telegram_handle} was not found."
            )


        current_tasks = pair[
            "task_completed"
        ]


        if current_tasks == "_":

            completed_tasks = []

        else:

            completed_tasks = [
                task.strip().lower()

                for task in current_tasks.split(",")

                if task.strip()
            ]


        # Prevent the same task being completed twice.
        if task_name in completed_tasks:
            return False


        completed_tasks.append(
            task_name
        )


        # ["movies", "tiktok"]
        #
        # becomes:
        #
        # "movies, tiktok"
        new_task_completed = ", ".join(
            completed_tasks
        )


        points = TASKS[
            task_name
        ]["points"]


        # Update both completed tasks and score.
        self.conn.execute(
            """
            UPDATE people

            SET task_completed = ?,

                score = score + ?

            WHERE id = ?
            """,

            (
                new_task_completed,
                points,
                pair["id"]
            )
        )


        self.conn.commit()

        return True


    # ========================================================
    # UNDO TASK
    # ========================================================

    def undo_task(
        self,
        telegram_handle,
        task_name
    ):

        if telegram_handle is None:
            return False


        telegram_handle = (
            telegram_handle
            .lstrip("@")
            .lower()
        )


        task_name = (
            task_name
            .strip()
            .lower()
        )


        # Check task exists.
        if task_name not in TASKS:

            raise ValueError(
                f"Unknown task: {task_name}"
            )


        pair = self.get_person(
            telegram_handle
        )


        if pair is None:

            raise ValueError(
                f"User @{telegram_handle} was not found."
            )


        current_tasks = pair[
            "task_completed"
        ]


        # Nothing to undo.
        if current_tasks == "_":
            return False


        completed_tasks = [
            task.strip().lower()

            for task in current_tasks.split(",")

            if task.strip()
        ]


        # Cannot undo a task that wasn't completed.
        if task_name not in completed_tasks:
            return False


        completed_tasks.remove(
            task_name
        )


        # If there are no tasks left,
        # store "_" again.
        if len(completed_tasks) == 0:

            new_task_completed = "_"

        else:

            new_task_completed = ", ".join(
                completed_tasks
            )


        points = TASKS[
            task_name
        ]["points"]


        # Remove the task and deduct points.
        self.conn.execute(
            """
            UPDATE people

            SET task_completed = ?,

                score = score - ?

            WHERE id = ?
            """,

            (
                new_task_completed,
                points,
                pair["id"]
            )
        )


        self.conn.commit()

        return True


    # ========================================================
    # CLOSE DATABASE
    # ========================================================

    def close(self):

        self.conn.close()