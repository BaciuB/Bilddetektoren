import csv
from collections import defaultdict
from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parent
from settings import RESULTS_FOLDER

LABELS_FILE = PROJECT_FOLDER / "data" / "image_labels.csv"
DETECTOR_FILE = RESULTS_FOLDER / "detector_results.csv"
PARTICIPANTS_FOLDER = RESULTS_FOLDER / "participants"
SUMMARY_FILE = RESULTS_FOLDER / "accuracy_summary.csv"

ANSWER_MAP = {
    "Reală": "real",
    "Generată cu AI": "ai",
    "Nu știu": "unknown",
}


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        return list(csv.DictReader(csv_file))


def main():
    for path in [LABELS_FILE, DETECTOR_FILE]:
        if not path.is_file():
            print(f"Lipsește fișierul: {path}")
            return

    participant_files = sorted(PARTICIPANTS_FOLDER.glob("*.csv"))

    if not participant_files:
        print("Nu există răspunsuri. Completează întâi testul în interfață.")
        return

    labels = {}

    for row in read_csv(LABELS_FILE):
        image_name = row["image"]
        label = row["label"]

        if label not in {"real", "ai"}:
            raise ValueError(f"Etichetă invalidă pentru {image_name}: {label}")

        if image_name in labels:
            raise ValueError(f"Imagine repetată în etichete: {image_name}")

        labels[image_name] = label

    detector_predictions = {}

    for row in read_csv(DETECTOR_FILE):
        key = (row["image"], row["version"])

        if key in detector_predictions:
            raise ValueError(f"Rezultat repetat pentru detector: {key}")

        if row["prediction"] not in {"real", "ai"}:
            raise ValueError(f"Predicție invalidă pentru {key}")

        detector_predictions[key] = row["prediction"]

    statistics = defaultdict(
        lambda: {"total": 0, "correct": 0, "unknown": 0}
    )

    for participant_file in participant_files:
        for row in read_csv(participant_file):
            image_name = row["image"]
            version = row["version"]
            key = (image_name, version)

            if image_name not in labels:
                raise ValueError(f"Lipsește eticheta pentru {image_name}")

            if key not in detector_predictions:
                raise ValueError(f"Lipsește rezultatul detectorului pentru {key}")

            if row["answer"] not in ANSWER_MAP:
                raise ValueError(f"Răspuns necunoscut în {participant_file.name}")

            true_label = labels[image_name]
            human_prediction = ANSWER_MAP[row["answer"]]
            detector_prediction = detector_predictions[key]

            for source, prediction in [
                ("human", human_prediction),
                ("detector", detector_prediction),
            ]:
                group = statistics[(source, version)]
                group["total"] += 1
                group["correct"] += int(prediction == true_label)
                group["unknown"] += int(prediction == "unknown")

    if not statistics:
        print("Fișierele participanților nu conțin răspunsuri.")
        return

    rows = []

    for (source, version), values in sorted(statistics.items()):
        accuracy = 100 * values["correct"] / values["total"]

        rows.append({
            "source": source,
            "version": version,
            "total": values["total"],
            "correct": values["correct"],
            "unknown": values["unknown"],
            "accuracy_percent": round(accuracy, 2),
        })

        print(
            f"{source} | {version} | "
            f"{values['correct']}/{values['total']} corecte | "
            f"{accuracy:.2f}%"
        )
    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)
    temporary_file = SUMMARY_FILE.with_suffix(".tmp")

    with temporary_file.open(
        "w", newline="", encoding="utf-8-sig"
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "source",
                "version",
                "total",
                "correct",
                "unknown",
                "accuracy_percent",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    temporary_file.replace(SUMMARY_FILE)
    print(f"\nTabel salvat în {SUMMARY_FILE}")


if __name__ == "__main__":
    main()