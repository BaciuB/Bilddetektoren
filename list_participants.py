from analyze_results import (
    ANSWER_MAP,
    LABELS_FILE,
    PARTICIPANTS_FOLDER,
    read_csv,
)
from main import QUALITIES


def main():
    if not LABELS_FILE.is_file():
        raise SystemExit("Lipsește data/image_labels.csv.")

    expected_images = {
        row["image"] for row in read_csv(LABELS_FILE)
    }

    if not expected_images:
        raise SystemExit("Lista imaginilor este goală.")

    participant_files = sorted(PARTICIPANTS_FOLDER.glob("*.csv"))

    if not participant_files:
        print("Nu există participanți în modul selectat.")
        return

    allowed_versions = {"original"}
    allowed_versions.update(f"Q{quality}" for quality in QUALITIES)

    completed_count = 0

    print(f"\nParticipanți din {PARTICIPANTS_FOLDER}\n")

    for participant_file in participant_files:
        rows = read_csv(participant_file)

        name = participant_file.stem

        if rows:
            name = rows[0].get("participant_name") or name

        answered_images = [
            row.get("image", "") for row in rows
        ]

        valid_answers = all(
            row.get("answer") in ANSWER_MAP
            and row.get("version") in allowed_versions
            for row in rows
        )

        is_complete = (
            len(rows) == len(expected_images)
            and set(answered_images) == expected_images
            and valid_answers
        )

        if is_complete:
            status = "TERMINAT"
            completed_count += 1
        else:
            status = "INCOMPLET / DE VERIFICAT"

        print(
            f"{name} | {status} | "
            f"{len(rows)}/{len(expected_images)} răspunsuri"
        )
        print(f"  Fișier: {participant_file.name}")

    print(f"\nSesiuni înregistrate: {len(participant_files)}")
    print(f"Sesiuni terminate: {completed_count}")
    print(
        f"Sesiuni incomplete / de verificat: "
        f"{len(participant_files) - completed_count}"
    )


if __name__ == "__main__":
    main()