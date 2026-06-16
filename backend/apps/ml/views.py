from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from apps.authentication.rbac import role_required
from apps.ml.predict import predict_risk
from apps.ml.ml_schema import (
    FeatureSchemaMismatch,
    get_training_feature_schema,
    prediction_feature_schema_from_patient_data,
    validate_feature_schema,
)
from apps.ml.models import ModelVersion, PredictionLog
from apps.patients.models import Patient


def _json_error(message: str, *, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


def _require_fields(payload: dict, fields: list[str]) -> None:
    missing = [f for f in fields if f not in payload or payload[f] in (None, "")]
    if missing:
        raise ValueError(f"Faltan campos: {', '.join(missing)}")


@login_required
@role_required("Administrador", "Médico")
@require_GET
def model_info(request):
    version = ModelVersion.objects.filter(is_active=True).order_by("-created_at").first()

    if version is None:
        return _json_error("No hay modelo activo", status=404)

    return JsonResponse(
        {
            "version": version.version,
            "accuracy": version.accuracy,
            "precision": version.precision,
            "recall": version.recall,
            "f1_score": version.f1_score,
            "dataset_size": version.dataset_size,
            "fecha_entrenamiento": version.created_at.isoformat(),
        }
    )


def _safe_artifact_path(base_path: str, artifact_name: str) -> str:
    # No normalizamos: almacenamos referencias tal como se generan en train.py.
    if not base_path:
        return ""
    # base_path apunta a apps/ml/logs/model_versions/<version>/metadata.json
    # Reemplazamos el archivo por el artefacto requerido.
    if base_path.endswith("metadata.json"):
        return base_path[: -len("metadata.json")] + artifact_name
    return base_path.rstrip("/") + "/" + artifact_name


@login_required
@role_required("Administrador", "Médico", "Analista")
@require_GET
def model_versions(request):
    versions = ModelVersion.objects.all().order_by("-created_at")
    payload = []
    for v in versions:
        metadata_path = v.metadata_path or ""
        payload.append(
            {
                "version": v.version,
                "created_at": v.created_at.isoformat(),
                "algorithm": v.algorithm,
                "dataset_size": v.dataset_size,
                "feature_schema": v.feature_schema,
                "accuracy": v.accuracy,
                "precision": v.precision,
                "recall": v.recall,
                "f1_score": v.f1_score,
                "metadata_path": metadata_path,
                "classification_report_path": _safe_artifact_path(metadata_path, "classification_report.txt"),
                "confusion_matrix_path": _safe_artifact_path(metadata_path, "confusion_matrix.png"),
                "model_path": v.model_path,
                "is_active": v.is_active,
            }
        )

    return JsonResponse({"ok": True, "versions": payload})


@login_required
@role_required("Administrador", "Médico")
@require_http_methods(["POST"])
def predicciones_single(request):
    """POST /api/ml/predicciones/

    Valida payload mínimo para ejecutar predicción.

    Campos requeridos:
    - edad (int)
    - imc (float)
    - presion_sistolica (int)
    - presion_diastolica (int)
    - glucosa (float)
    - colesterol (float)
    """
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return _json_error("payload JSON inválido")

    try:
        _require_fields(
            payload,
            [
                "edad",
                "imc",
                "presion_sistolica",
                "presion_diastolica",
                "glucosa",
                "colesterol",
            ],
        )

        # Validación automática de esquema de features (auditoría)
        training_schema = get_training_feature_schema().columns
        prediction_schema = prediction_feature_schema_from_patient_data(payload)
        validate_feature_schema(training_schema, prediction_schema)

        risk_label, confidence, proba_map = predict_risk(payload)

        # Persistencia de predicción (si viene patient_id)
        patient_id = payload.get("patient_id")
        model_version = ModelVersion.objects.filter(is_active=True).order_by("-created_at").first()

        patient_obj = None
        if patient_id is not None:
            patient_obj = Patient.objects.filter(id_paciente=patient_id).first()
            if patient_obj is None:
                return _json_error(f"patient_id no existe: {patient_id}", status=404)

        # Para compatibilidad, si no hay patient_id no rompemos el flujo.
        # Guardamos el log solo si podemos resolver paciente y modelo activo.
        if patient_obj is not None and model_version is not None:
            PredictionLog.objects.create(
                patient=patient_obj,
                model_version=model_version,
                prediction=str(risk_label),
                probability=float(confidence),
            )

        return JsonResponse(
            {
                "ok": True,
                "riesgo_enfermedad": str(risk_label),
                "confidence": float(confidence),
                "probabilidades": proba_map,
            }
        )
    except FeatureSchemaMismatch as e:
        return _json_error(f"Feature schema mismatch: {str(e)}", status=409)
    except FileNotFoundError as e:
        return _json_error(str(e), status=500)
    except Exception as e:
        return _json_error(str(e), status=400)

