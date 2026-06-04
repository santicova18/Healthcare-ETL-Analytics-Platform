import joblib
import pandas as pd
import os

def predict_risk(patient_data):
    """
    Recibe un diccionario con los datos del paciente:
    {'edad': 45, 'imc': 28.5, 'presion_sistolica': 120, ...}
    
    Retorna: String con la predicción de riesgo (Bajo, Medio, Alto, Crítico)
    """
    # 1. Cargar modelo, scaler y codificador
    model_path = 'apps/ml/models/risk_model.pkl'
    scaler_path = 'apps/ml/models/scaler.pkl'
    encoder_path = 'apps/ml/models/label_encoder.pkl'
    
    if not os.path.exists(model_path):
        raise FileNotFoundError("El modelo no ha sido entrenado aún. Ejecuta train_model primero.")
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    le = joblib.load(encoder_path)
    
    # 2. Convertir diccionario a DataFrame con ORDEN CORRECTO
    feature_columns = ['edad', 'imc', 'presion_sistolica', 'presion_diastolica', 'glucosa', 'colesterol']
    df_input = pd.DataFrame([patient_data])[feature_columns]
    
    # Mantener nombres de features para evitar warnings
    df_input.columns = feature_columns
    
    # 3. ESCALAR con el mismo scaler del entrenamiento
    df_scaled = scaler.transform(df_input)
    
    # 4. Realizar predicción
    prediction = model.predict(df_scaled)
    
    # 5. Obtener probabilidades para mayor confianza
    prediction_proba = model.predict_proba(df_scaled)[0]
    
    # 6. Decodificar la predicción
    risk_label = le.inverse_transform(prediction)[0]
    confidence = prediction_proba[prediction[0]]
    
    # 7. Retornar resultado
    return risk_label, confidence, dict(zip(le.classes_, prediction_proba))