import hashlib
import json
import random
import sqlite3
from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parent
DATABASE_FILE = PROJECT_FOLDER / "results" / "assignments.sqlite"


def assign_trials(version_groups, participant_id):
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Identifică setul de imagini și versiunile disponibile.
    configuration = [
        [(item["image"], item["version"]) for item in group]
        for group in version_groups
    ]

    study_key = hashlib.sha256(
        json.dumps(configuration).encode("utf-8")
    ).hexdigest()

    with sqlite3.connect(DATABASE_FILE, timeout=30) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                study_key TEXT NOT NULL,
                participant_id TEXT NOT NULL,
                position INTEGER NOT NULL,
                PRIMARY KEY (study_key, participant_id),
                UNIQUE (study_key, position)
            )
        """)

        connection.execute("BEGIN IMMEDIATE")

        existing = connection.execute(
            """
            SELECT position FROM participants
            WHERE study_key = ? AND participant_id = ?
            """,
            (study_key, participant_id),
        ).fetchone()

        if existing:
            position = existing[0]
        else:
            position = connection.execute(
                """
                SELECT COUNT(*) FROM participants
                WHERE study_key = ?
                """,
                (study_key,),
            ).fetchone()[0]

            connection.execute(
                "INSERT INTO participants VALUES (?, ?, ?)",
                (study_key, participant_id, position),
            )

    trials = []

    for group in version_groups:
        cycle, slot = divmod(position, len(group))

        seed = f"{study_key}:{group[0]['image']}:{cycle}"
        generator = random.Random(seed)

        shuffled_versions = group.copy()
        generator.shuffle(shuffled_versions)

        trials.append(shuffled_versions[slot])

    random.shuffle(trials)
    return trials