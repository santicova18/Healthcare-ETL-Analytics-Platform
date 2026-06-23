from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Patient
from apps.ml.predict import predict_risk

@receiver(pre_save, sender=Patient)
def auto_predict_risk(sender, instance, **kwargs):
    # Solo predecimos si el paciente no tiene riesgo asignado aún
    if not instance.riesgo_enfermedad:
        patient_data = {
            'edad': instance.edad,
            'imc': instance.imc,
            'presion_sistolica': instance.presion_sistolica,
            'presion_diastolica': instance.presion_diastolica,
            'glucosa': instance.glucosa,
            'colesterol': instance.colesterol,
        }
        try:
            risk_label, _, _ = predict_risk(patient_data)
            instance.riesgo_enfermedad = str(risk_label)
        except FileNotFoundError:
            pass


