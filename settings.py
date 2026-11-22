from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parent

EXPERIMENT_MODE = "test"

if EXPERIMENT_MODE not in {"test", "final"}:
    raise ValueError("EXPERIMENT_MODE trebuie să fie test sau final.")

RESULTS_FOLDER = PROJECT_FOLDER / "results" / EXPERIMENT_MODE