import csv
from pathlib import Path

from main import IMAGE_FORMATS

PROJECT_FOLDER = Path(__file__).resolve().parent
IMAGE_FOLDER = PROJECT_FOLDER / "data" / "originals"
LABELS_FILE = PROJECT_FOLDER / "data" / "image_labels.csv"


def main():
    if not IMAGE_FOLDER.is_dir():
        raise SystemExit("Nu există folderul data/originals.")

    images = sorted(
        path for path in IMAGE_FOLDER.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_FORMATS
    )

    if not images:
        raise SystemExit("Nu există imagini în data/originals.")

    existing_rows = {}
    fieldnames = ["image", "label", "source"]

    if LABELS_FILE.is_file():
        with LABELS_FILE.open(
            newline="", encoding="utf-8-sig"
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            if not set(fieldnames).issubset(reader.fieldnames or []):
                raise SystemExit(
                    "CSV-ul trebuie să conțină coloanele image, label și source."
                )

            fieldnames = reader.fieldnames

            for row in reader:
                image_name = (row["image"] or "").strip()

                if not image_name or None in row:
                    raise SystemExit("Există un rând invalid în CSV.")

                if image_name in existing_rows:
                    raise SystemExit(
                        f"Imagine repetată în CSV: {image_name}"
                    )

                row["image"] = image_name
                row["label"] = (row["label"] or "").strip()
                row["source"] = (row["source"] or "").strip()

                if row["label"] not in {"", "real", "ai"}:
                    raise SystemExit(
                        f"Etichetă invalidă pentru {image_name}. "
                        "Folosește real sau ai."
                    )

                existing_rows[image_name] = row

    added = 0

    for image_path in images:
        if image_path.name not in existing_rows:
            existing_rows[image_path.name] = {
                column: "" for column in fieldnames
            }
            existing_rows[image_path.name]["image"] = image_path.name
            added += 1

    temporary_file = LABELS_FILE.with_suffix(".tmp")

    with temporary_file.open(
        "w", newline="", encoding="utf-8-sig"
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_rows.values())

    temporary_file.replace(LABELS_FILE)

    print(f"Imagini noi adăugate în listă: {added}")

    incomplete = [
        image_path.name
        for image_path in images
        if not existing_rows[image_path.name]["label"]
        or not existing_rows[image_path.name]["source"]
    ]

    if incomplete:
        print("Completează label și source pentru:")

        for image_name in incomplete:
            print(f"  - {image_name}")

        raise SystemExit(1)

    print("Toate imaginile actuale au etichetă și proveniență.")


if __name__ == "__main__":
    main()