import csv
from pathlib import Path

import matplotlib.pyplot as plt

PROJECT_FOLDER = Path(__file__).resolve().parent
from settings import RESULTS_FOLDER
SUMMARY_FILE = RESULTS_FOLDER / "accuracy_summary.csv"
CHART_FILE = RESULTS_FOLDER / "accuracy_comparison.png"

VERSION_ORDER = ["original", "Q40", "Q20", "Q10", "Q1"]


def main():
    if not SUMMARY_FILE.is_file():
        print("Rulează mai întâi analyze_results.py.")
        return

    with SUMMARY_FILE.open(
        newline="", encoding="utf-8-sig"
    ) as csv_file:
        rows = list(csv.DictReader(csv_file))

    results = {
        (row["source"], row["version"]): row
        for row in rows
    }

    versions = [
        version for version in VERSION_ORDER
        if ("human", version) in results
        and ("detector", version) in results
    ]

    if not versions:
        print("Nu există rezultate pentru comparație.")
        return

    human_scores = [
        float(results[("human", version)]["accuracy_percent"])
        for version in versions
    ]

    detector_scores = [
        float(results[("detector", version)]["accuracy_percent"])
        for version in versions
    ]

    labels = [
        f"{version}\n"
        f"n={results[('human', version)]['total']}"
        for version in versions
    ]

    positions = list(range(len(versions)))
    bar_width = 0.36

    figure, axis = plt.subplots(figsize=(9, 5))

    human_bars = axis.bar(
        [position - bar_width / 2 for position in positions],
        human_scores,
        width=bar_width,
        label="Oameni",
        color="#2563EB",
    )

    detector_bars = axis.bar(
        [position + bar_width / 2 for position in positions],
        detector_scores,
        width=bar_width,
        label="Detector",
        color="#EA580C",
    )

    axis.bar_label(human_bars, fmt="%.1f", padding=3)
    axis.bar_label(detector_bars, fmt="%.1f", padding=3)

    axis.set_xticks(positions, labels)
    axis.set_ylim(0, 110)
    axis.set_yticks(range(0, 101, 20))
    axis.set_ylabel("Răspunsuri corecte (%)")
    axis.set_xlabel("Versiunea imaginii și numărul răspunsurilor evaluate")
    axis.set_title("Oameni și detector — sesiuni de test")
    axis.legend()

    axis.set_axisbelow(True)
    axis.grid(axis="y", alpha=0.25)

    figure.tight_layout()
    figure.savefig(CHART_FILE, dpi=200)
    plt.close(figure)

    print(f"Grafic salvat în {CHART_FILE}")


if __name__ == "__main__":
    main()