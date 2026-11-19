from pathlib import Path

import streamlit as st

PROJECT_FOLDER = Path(__file__).resolve().parent
IMAGE_FOLDER = PROJECT_FOLDER / "data" / "originals"
IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}

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

