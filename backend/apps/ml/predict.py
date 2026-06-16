import os
from pathlib import Path

import joblib
import pandas as pd

_ML_DIR = Path(__file__).resolve().parent
_MODELS_DIR = _ML_DIR / "models"


def _artifact_path(name: str) -> Path:
    return _MODELS_DIR / name


def predict_risk(patient_data):
    """
    Recibe un diccionario con los datos del paciente:
    {'edad': 45, 'imc': 28.5, 'presion_sistolica': 120, ...}

    Retorna: (risk_label, confidence, proba_map)
    """
    model_path = _artifact_path("risk_model.pkl")
    scaler_path = _artifact_path("scaler.pkl")
    encoder_path = _artifact_path("label_encoder.pkl")

    if not model_path.exists():
        raise FileNotFoundError(
            "El modelo no ha sido entrenado aún. Ejecuta: python manage.py train_model"
        )
    if not scaler_path.exists():
        raise FileNotFoundError(f"Scaler no encontrado: {scaler_path}")
    if not encoder_path.exists():
        raise FileNotFoundError(f"Label encoder no encontrado: {encoder_path}")

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    le = joblib.load(encoder_path)

    feature_columns = [
        "edad",
        "imc",
        "presion_sistolica",
        "presion_diastolica",
        "glucosa",
        "colesterol",
    ]
    df_input = pd.DataFrame([patient_data])[feature_columns]
    df_input.columns = feature_columns

    df_scaled = scaler.transform(df_input)
    prediction = model.predict(df_scaled)
    prediction_proba = model.predict_proba(df_scaled)[0]

    risk_label = le.inverse_transform(prediction)[0]
    confidence = prediction_proba[prediction[0]]

    return risk_label, confidence, dict(zip(le.classes_, prediction_proba))
