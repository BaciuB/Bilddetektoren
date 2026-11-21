import csv
from pathlib import Path

from PIL import Image, ImageOps
from transformers import pipeline

from main import INPUT_FOLDER, OUTPUT_FOLDER, QUALITIES, IMAGE_FORMATS

PROJECT_FOLDER = Path(__file__).resolve().parent
RESULTS_FOLDER = PROJECT_FOLDER / "results"
RESULTS_FILE = RESULTS_FOLDER / "detector_results.csv"

MODEL_NAME = "Ateeqq/ai-vs-human-image-detector"

LABEL_MAP = {
    "ai": "ai",
    "hum": "real",
}


def main():
    if not INPUT_FOLDER.exists():
        print("Nu există folderul cu imaginile originale.")
        return

    originals = sorted(
        path for path in INPUT_FOLDER.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_FORMATS
    )

    if not originals:
        print("Nu am găsit imagini în data/originals.")
        return

    trials = []

    for original_path in originals:
        trials.append((original_path.name, "original", original_path))

        for quality in QUALITIES:
            compressed_path = (
                OUTPUT_FOLDER
                / f"quality_{quality}"
                / f"{original_path.stem}_q{quality}.jpg"
            )

            if not compressed_path.is_file():
                print(f"Lipsește: {compressed_path}")
                print("Rulează main.py pentru a genera compresiile.")
                return

            trials.append((
                original_path.name,
                f"Q{quality}",
                compressed_path,
            ))

    print("Se încarcă detectorul.")
    print("La prima rulare se descarcă modelul. Ai nevoie de internet.")

    detector = pipeline(
        "image-classification",
        model=MODEL_NAME,
        device=-1,
    )

    rows = []

    for index, (image_name, version, image_path) in enumerate(
        trials, start=1
    ):
        with Image.open(image_path) as opened_image:
            image = ImageOps.exif_transpose(opened_image).convert("RGB")
            predictions = detector(image, top_k=2)

        scores = {
            LABEL_MAP[prediction["label"]]: prediction["score"]
            for prediction in predictions
        }

        predicted_label = max(scores, key=scores.get)

        rows.append({
            "image": image_name,
            "version": version,
            "prediction": predicted_label,
            "score_ai": scores["ai"],
            "score_real": scores["real"],
            "model": MODEL_NAME,
        })

        print(
            f"[{index}/{len(trials)}] "
            f"{image_name} | {version} | {predicted_label}"
        )

    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)
    temporary_file = RESULTS_FILE.with_suffix(".tmp")

    with temporary_file.open(
        "w", newline="", encoding="utf-8-sig"
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "image",
                "version",
                "prediction",
                "score_ai",
                "score_real",
                "model",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    temporary_file.replace(RESULTS_FILE)

    print(f"Rezultatele au fost salvate în {RESULTS_FILE}")


if __name__ == "__main__":
    main()