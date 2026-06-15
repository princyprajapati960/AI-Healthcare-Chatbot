"""TF-IDF + Logistic Regression triage classifier."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

MODEL_DIR = Path(__file__).resolve().parents[2] / "models"
MODEL_PATH = MODEL_DIR / "triage_model.pkl"
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "triage_symptoms.csv"

_pipeline: Pipeline | None = None


def train_and_save() -> Pipeline:
    df = pd.read_csv(DATA_PATH)
    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words="english")),
            ("clf", LogisticRegression(max_iter=1000, multi_class="multinomial")),
        ]
    )
    pipeline.fit(df["symptoms"], df["department"])
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    return pipeline


def load_model() -> Pipeline:
    global _pipeline
    if _pipeline is not None:
        return _pipeline
    if not MODEL_PATH.exists():
        _pipeline = train_and_save()
    else:
        _pipeline = joblib.load(MODEL_PATH)
    return _pipeline


def predict_department(symptoms: str) -> tuple[str, float]:
    pipeline = load_model()
    proba = pipeline.predict_proba([symptoms])[0]
    classes = pipeline.classes_
    idx = proba.argmax()
    return str(classes[idx]), float(proba[idx])
