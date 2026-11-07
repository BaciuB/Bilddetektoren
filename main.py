from pathlib import Path

from PIL import Image, ImageOps


PROJECT_FOLDER = Path(__file__).parent
INPUT_FOLDER = PROJECT_FOLDER / "data" / "originals"
OUTPUT_FOLDER = PROJECT_FOLDER / "data" / "compressed"
QUALITIES = (40, 20, 10, 1)
IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}


def main():
    INPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    images = sorted(
        path for path in INPUT_FOLDER.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_FORMATS
    )

    if not images:
        print("Folderul data/originals este gol. Pune acolo o imagine JPG sau PNG.")
        return

    for image_path in images:
        with Image.open(image_path) as original:
            image = ImageOps.exif_transpose(original).convert("RGB")

            for quality in QUALITIES:
                quality_folder = OUTPUT_FOLDER / f"quality_{quality}"
                quality_folder.mkdir(parents=True, exist_ok=True)

                output_path = quality_folder / f"{image_path.stem}_q{quality}.jpg"
                image.save(output_path, "JPEG", quality=quality)

                print(f"Creat: {output_path.relative_to(PROJECT_FOLDER)}")


if __name__ == "__main__":
    main()