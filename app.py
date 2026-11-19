from pathlib import Path
import csv
import uuid

import streamlit as st

PROJECT_FOLDER = Path(__file__).resolve().parent
IMAGE_FOLDER = PROJECT_FOLDER / "data" / "originals"
IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}

RESULTS_FOLDER = PROJECT_FOLDER / "results" / "participants"

def save_answers(answers, participant_id):
    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)

    output_file = RESULTS_FOLDER / f"{participant_id}.csv"
    temporary_file = RESULTS_FOLDER / f"{participant_id}.tmp"

    with temporary_file.open("w", newline="", encoding ="utf-8-sig")as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["participant_id", "image", "version", "answer"],
        )
        writer.writeheader()

        for answer in answers:
            writer.writerow({
            "participant_id": participant_id,
            **answer,
        })

    temporary_file.replace(output_file)

if"participant_id" not in st.session_state:
    st.session_state.participant_id = uuid.uuid4().hex

st.set_page_config(page_title="Experiment imagini", layout="centered")

st.title("Reală sau generată cu AI?")
st.write("Privește imaginea și alege răspunsul care ți se pare potrivit.")

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

if "image_index" not in st.session_state:
    st.session_state.image_index = 0
    st.session_state.answers = []

index = st.session_state.image_index

if index >= len(images):
    st.success("Ai terminat! Mulțumim pentru participare.")
    st.write(f"Ai răspuns la {len(st.session_state.answers)} imagini.")
    st.stop()

image_path = images[index]

st.write(f"Imaginea {index + 1} din {len(images)}")
st.progress(index / len(images))
st.image(str(image_path))

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
        st.session_state.answers.append({
            "image": image_path.name,
            "version": "original",
            "answer": answer,
        })
        st.session_state.image_index += 1
        st.rerun()