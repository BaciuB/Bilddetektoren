import csv
from pathlib import Path

from PIL import Image

from main import INPUT_FOLDER, OUTPUT_FOLDER, QUALITIES, IMAGE_FORMATS

PROJECT_FOLDER = Path(__file__).resolve().parent
LABELS_FILE = PROJECT_FOLDER / "data" / "image_labels.csv"


def main():
    if not INPUT_FOLDER.is_dir():
        raise SystemExit("Nu există folderul data/originals.")

    if not LABELS_FILE.is_file():
        raise SystemExit("Lipsește data/image_labels.csv.")

    images = sorted(
        path for path in INPUT_FOLDER.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_FORMATS
    )

    if not images:
        raise SystemExit("Nu există imagini în data/originals.")

    errors = []
    labels = {}

    with LABELS_FILE.open(
        newline="", encoding="utf-8-sig"
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        required_columns = {"image", "label", "source"}

        if not required_columns.issubset(reader.fieldnames or []):
            raise SystemExit(
                "CSV-ul trebuie să aibă coloanele image, label și source."
            )

        for row in reader:
            if None in row:
                errors.append("CSV-ul conține un rând cu prea multe valori.")
                continue

            image_name = (row["image"] or "").strip()
            label = (row["label"] or "").strip()
            source = (row["source"] or "").strip()

            if not image_name:
                errors.append("Există un rând fără numele imaginii.")
                continue

            if image_name in labels:
                errors.append(f"Imagine repetată în CSV: {image_name}")

            if label not in {"real", "ai"}:
                errors.append(f"Etichetă invalidă pentru {image_name}.")

            if not source:
                errors.append(f"Lipsește proveniența pentru {image_name}.")

            labels[image_name] = label

    image_names = {path.name for path in images}

    for image_name in sorted(image_names - labels.keys()):
        errors.append(f"Lipsește eticheta din CSV: {image_name}")

    for image_name in sorted(labels.keys() - image_names):
        errors.append(f"Imagine din CSV absentă din originals: {image_name}")

    # Două originale cu aceeași bază de nume ar produce
    # același nume pentru fișierele comprimate.
    stems = set()

    for image_path in images:
        stem = image_path.stem.casefold()

        if stem in stems:
            errors.append(
                f"Nume de bază repetat: {image_path.stem}. "
                "Redenumește originalele pentru a evita suprascrierea."
            )

        stems.add(stem)

        paths_to_check = [image_path]

        for quality in QUALITIES:
            paths_to_check.append(
                OUTPUT_FOLDER
                / f"quality_{quality}"
                / f"{image_path.stem}_q{quality}.jpg"
            )

        for path in paths_to_check:
            if not path.is_file():
                errors.append(f"Lipsește fișierul: {path}")
                continue

            try:
                with Image.open(path) as image:
                    image.verify()

                with Image.open(path) as image:
                    image.load()

            except (OSError, SyntaxError, ValueError) as error:
                errors.append(f"Imagine imposibil de citit: {path} ({error})")

    if errors:
        print("\nProbleme găsite:")

        for error in errors:
            print(f"  - {error}")

        raise SystemExit(1)

    real_count = sum(labels[name] == "real" for name in image_names)
    ai_count = sum(labels[name] == "ai" for name in image_names)

    print("Verificare reușită.")
    print(f"Originale: {len(images)}")
    print(f"Reale: {real_count} | AI: {ai_count}")
    print("Etichetele, proveniența și fișierele sunt completate și lizibile.")


if __name__ == "__main__":
    main()