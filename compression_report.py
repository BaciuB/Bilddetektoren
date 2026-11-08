import csv
from pathlib import Path

from PIL import Image, ImageOps
from main import INPUT_FOLDER, OUTPUT_FOLDER, QUALITIES, IMAGE_FORMATS


PROJECT_FOLDER = Path(__file__).parent
RESULTS_FOLDER = PROJECT_FOLDER / "results"
SUMMARY_FILE = RESULTS_FOLDER / "compression_summary.csv"


def get_image_details(image_path):
    with Image.open(image_path) as opened_image:
        image = ImageOps.exif_transpose(opened_image)
        width, height = image.size

    file_size_kb = round(image_path.stat().st_size / 1024, 2)
    return width, height, file_size_kb


def main():
    if not INPUT_FOLDER.exists():
        print("Folderul cu imaginile originale nu există. Rulează mai întâi main.py.")
        return

    original_images = sorted(
        path for path in INPUT_FOLDER.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_FORMATS
    )

    if not original_images:
        print("Nu am găsit imagini în data/originals.")
        return

    rows = []

    for original_path in original_images:
        width, height, size_kb = get_image_details(original_path)
        rows.append([original_path.name, "original", width, height, size_kb])

        for quality in QUALITIES:
            compressed_path = (
                OUTPUT_FOLDER
                / f"quality_{quality}"
                / f"{original_path.stem}_q{quality}.jpg"
            )

            if not compressed_path.exists():
                print(f"Varianta lipsește: {compressed_path.name}")
                continue

            width, height, size_kb = get_image_details(compressed_path)
            rows.append([
                original_path.name,
                f"Q{quality}",
                width,
                height,
                size_kb,
            ])

    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)

    with open(SUMMARY_FILE, "w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            "image",
            "version",
            "width_px",
            "height_px",
            "file_size_kb",
        ])
        writer.writerows(rows)

    print(f"Tabelul a fost salvat: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()