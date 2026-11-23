from pathlib import Path
import csv
import uuid
import random
from main import OUTPUT_FOLDER, QUALITIES
import streamlit as st
from assignment import assign_trials
import re
import unicodedata

PROJECT_FOLDER = Path(__file__).resolve().parent
IMAGE_FOLDER = PROJECT_FOLDER / "data" / "originals"
IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}

from settings import RESULTS_FOLDER as EXPERIMENT_RESULTS_FOLDER

RESULTS_FOLDER = EXPERIMENT_RESULTS_FOLDER / "participants"

def save_answers(answers, participant_id):
    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)

    output_file = (
        RESULTS_FOLDER / st.session_state.participant_filename
    )
    temporary_file = output_file.with_suffix(".tmp")

    with temporary_file.open(
        "w", newline="", encoding="utf-8-sig"
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "participant_id",
                "participant_name",
                "image",
                "version",
                "answer",
            ],
        )
        writer.writeheader()

        for answer in answers:
            writer.writerow({
                "participant_id": participant_id,
                "participant_name": st.session_state.participant_name,
                **answer,
            })

    temporary_file.replace(output_file)

st.set_page_config(page_title="Experiment imagini", layout="centered")

st.title("Reală sau generată cu AI?")
st.write("Privește imaginea și alege răspunsul care ți se pare potrivit.")

if "participant_name" not in st.session_state:
    with st.form("participant_registration"):
        name = st.text_input(
            "Numele tău",
            max_chars=80,
            placeholder="Prenume și nume",
        )

        start_test = st.form_submit_button("Începe testul")

    if start_test:
        participant_name = " ".join(name.split())

        if not participant_name:
            st.warning("Completează numele înainte să începi.")
            st.stop()

        normalized_name = unicodedata.normalize(
            "NFKD", participant_name
        )
        ascii_name = normalized_name.encode(
            "ascii", "ignore"
        ).decode("ascii")

        safe_name = re.sub(
            r"[^A-Za-z0-9]+", "_", ascii_name
        ).strip("_")

        safe_name = safe_name[:60] or "participant"

        try:
            RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)

            # Rezervă un nume de fișier liber pentru această sesiune.
            while True:
                participant_id = uuid.uuid4().hex
                filename = f"{safe_name}_{participant_id[:8]}.csv"
                participant_file = RESULTS_FOLDER / filename

                try:
                    with participant_file.open(
                        "x", encoding="utf-8-sig"
                    ):
                        pass
                    break
                except FileExistsError:
                    continue

        except OSError:
            st.error(
                "Nu am putut crea fișierul participantului. "
                "Încearcă din nou."
            )
            st.stop()

        st.session_state.participant_name = participant_name
        st.session_state.participant_id = participant_id
        st.session_state.participant_filename = filename

        st.session_state.pop("trials", None)
        st.session_state.image_index = 0
        st.session_state.answers = []

        st.rerun()

    st.stop()

if not IMAGE_FOLDER.exists():
    st.error("Nu am găsit folderul data/originals.")
    st.stop()

images = sorted(
    path for path in IMAGE_FOLDER.iterdir()
    if path.is_file() and path.suffix.lower() in IMAGE_FORMATS
)

if not images:
    st.warning("Adaugă imaginile de test în data/originals.")
    st.stop()

if "trials" not in st.session_state:
    version_groups = []

    for original_path in images:
        versions = [{
            "path": original_path,
            "image": original_path.name,
            "version": "original",
        }]

        for quality in QUALITIES:
            compressed_path = (
                OUTPUT_FOLDER
                / f"quality_{quality}"
                / f"{original_path.stem}_q{quality}.jpg"
            )

            if not compressed_path.is_file():
                st.error(
                    f"Lipsește varianta {compressed_path.name}. "
                    "Rulează main.py, apoi reîncarcă pagina."
                )
                st.stop()

            versions.append({
                "path": compressed_path,
                "image": original_path.name,
                "version": f"Q{quality}",
            })

        version_groups.append(versions)

    st.session_state.trials = assign_trials(
        version_groups,
        st.session_state.participant_id,
    )

trials = st.session_state.trials

if "image_index" not in st.session_state:
    st.session_state.image_index = 0
    st.session_state.answers = []

index = st.session_state.image_index

if index >= len(trials):
    st.success("Ai terminat! Mulțumim pentru participare.")
    st.write(f"Ai răspuns la {len(st.session_state.answers)} imagini.")
    st.stop()

current_trial = trials[index]

st.write(f"Imaginea {index + 1} din {len(trials)}")
st.progress(index / len(trials))
st.image(str(current_trial["path"]))

with st.form(key=f"question_{index}"):
    answer = st.radio(
        "Cum crezi că a fost creată imaginea?",
        ["Reală", "Generată cu AI", "Nu știu"],
        index=None,
    )

    submitted = st.form_submit_button("Următoarea")

if submitted:
    if answer is None:
        st.warning("Alege un răspuns înainte să continui.")
    else:
        new_answer = {
            "image": current_trial["image"],
            "version": current_trial["version"],
            "answer": answer,
        }

        updated_answers = st.session_state.answers + [new_answer]

        try:
            save_answers(
                updated_answers,
                st.session_state.participant_id,
            )
        except OSError:
            st.error(
                "Răspunsul nu a putut fi salvat. "
                "Apasă din nou Următoarea pentru a reîncerca."
            )
            st.stop()

        st.session_state.answers = updated_answers
        st.session_state.image_index += 1
        st.rerun()