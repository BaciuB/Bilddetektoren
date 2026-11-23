import subprocess
import sys
from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parent


def run_script(filename):
    print(f"\nSe rulează {filename}...", flush=True)

    subprocess.run(
        [sys.executable, str(PROJECT_FOLDER / filename)],
        cwd=PROJECT_FOLDER,
        check=True,
    )


def main():
    print("1. Pregătește imaginile și raportul de compresie")
    print("2. Pornește interfața pentru participanți")
    print("3. Rulează detectorul, statisticile și graficul")
    print("4. Actualizează doar statisticile și graficul")
    print("5. Vezi participanții și starea testelor")

    choice = input("\nAlege 1, 2, 3, 4 sau 5: ").strip()
    try:
        if choice == "1":
            run_script("main.py")
            run_script("prepare_labels.py")
            run_script("validate_data.py")
            run_script("compression_report.py")

        elif choice == "2":
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "streamlit",
                    "run",
                    str(PROJECT_FOLDER / "app.py"),
                ],
                cwd=PROJECT_FOLDER,
                check=True,
            )


        elif choice == "3":
            run_script("validate_data.py")
            run_script("run_detector.py")
            run_script("analyze_results.py")
            run_script("plot_results.py")

        elif choice == "4":
            run_script("analyze_results.py")
            run_script("plot_results.py")

        elif choice == "5":
            run_script("list_participants.py")
        else:
            print("Opțiune invalidă.")

    except subprocess.CalledProcessError:
        print("\nExecuția s-a oprit. Verifică eroarea afișată mai sus.")

    except KeyboardInterrupt:
        print("\nExecuție oprită.")


if __name__ == "__main__":
    main()