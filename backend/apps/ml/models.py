from __future__ import annotations

from django.conf import settings
from django.db import models


class ModelVersion(models.Model):
    version = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    algorithm = models.CharField(max_length=128, default="RandomForestClassifier")
    dataset_size = models.PositiveIntegerField(default=0)

    # Guardamos el esquema como JSON (lista/objeto) para auditoría
    feature_schema = models.JSONField(default=list)

    accuracy = models.FloatField(null=True, blank=True)
    precision = models.JSONField(null=True, blank=True)
    recall = models.JSONField(null=True, blank=True)
    f1_score = models.JSONField(null=True, blank=True)

    model_path = models.CharField(max_length=255, blank=True, default="")
    metadata_path = models.CharField(max_length=255, blank=True, default="")

    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"ModelVersion(version={self.version}, active={self.is_active})"


class PredictionLog(models.Model):
    # Mantener opcionalidad para compatibilidad cuando el cliente no envía patient_id
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="prediction_logs",
    )
    model_version = models.ForeignKey(
        ModelVersion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prediction_logs",
    )

    prediction = models.CharField(max_length=64)
    probability = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self) -> str:
        return (
            f"PredictionLog(patient={self.patient_id}, model_version={self.model_version_id}, "
            f"prediction={self.prediction}, prob={self.probability})"
        )

