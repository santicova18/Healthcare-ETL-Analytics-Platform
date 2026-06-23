# test_predict_cases.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ml.predict import predict_risk

def run_suite():
    test_cases = [
        {
            "nombre": "Paciente Saludable",
            "datos": {'edad': 25, 'imc': 22.0, 'presion_sistolica': 110, 'presion_diastolica': 70, 'glucosa': 90, 'colesterol': 150},
            "esperado": "Bajo" 
        },
        {
            "nombre": "Paciente con Riesgo",
            "datos": {'edad': 55, 'imc': 32.0, 'presion_sistolica': 145, 'presion_diastolica': 95, 'glucosa': 140, 'colesterol': 240},
            "esperado": "Medio/Alto"
        },
        {
            "nombre": "Paciente Crítico",
            "datos": {'edad': 75, 'imc': 35.0, 'presion_sistolica': 180, 'presion_diastolica': 110, 'glucosa': 280, 'colesterol': 300},
            "esperado": "Crítico"
        }
    ]

    print(f"\n{'Caso':<25} | {'Predicción':<12} | {'Confianza':<10} | {'Esperado':<12}")
    print("-" * 65)
    
    for case in test_cases:
        try:
            risk_label, confidence, probabilities = predict_risk(case['datos'])
            prob_str = " | ".join([f"{label}: {prob:.1%}" for label, prob in probabilities.items()])
            print(f"{case['nombre']:<25} | {risk_label:<12} | {confidence:<9.1%} | {case['esperado']:<12}")
            print(f"  → Probabilidades: {prob_str}")
        except Exception as e:
            print(f"{case['nombre']:<25} | ERROR: {str(e)}")

if __name__ == "__main__":
    run_suite()