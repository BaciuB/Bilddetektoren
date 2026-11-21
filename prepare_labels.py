import csv
from pathlib import Path

from main import IMAGE_FORMATS

PROJECT_FOLDER = Path(__file__).resolve().parent
IMAGE_FOLDER = PROJECT_FOLDER / "data" / "originals"
LABELS_FILE = PROJECT_FOLDER / "data" / "image_labels.csv"


def main():
    if LABELS_FILE.exists():
        print("Lista există deja. O poți modifica manual.")
        return

    if not IMAGE_FOLDER.exists():
        print("Nu există folderul data/originals.")
        return

    images = sorted(
        path for path in IMAGE_FOLDER.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_FORMATS
    )

    if not images:
        print("Nu am găsit imagini în data/originals.")
        return

    with LABELS_FILE.open(
        "w", newline="", encoding="utf-8-sig"
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["image", "label", "source"])

        for image_path in images:
            writer.writerow([
                image_path.name,
                "real",
                "Fotografie proprie - test",
            ])

    print(f"Am înregistrat {len(images)} imagini.")
    print(f"Lista a fost salvată în {LABELS_FILE}")


if __name__ == "__main__":
    main()