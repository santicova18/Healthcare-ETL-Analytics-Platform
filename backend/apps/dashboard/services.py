from __future__ import annotations

from typing import Any, Dict, List

from django.db.models import Count
from django.utils import timezone

from apps.analytics.services import kpis_clinicos, segmentaciones
from apps.etl.models import ETLRun
from apps.ml.predict import predict_risk
from apps.patients.models import Patient


def dashboard_kpis() -> Dict[str, Any]:
    """KPIs obligatorios para Dashboard."""
    kpis = kpis_clinicos()

    # Map de requisitos del enunciado
    return {
        "total_pacientes": kpis.get("total_pacientes", 0),
        "pacientes_criticos": kpis.get("criticos", 0),
        "hipertensos": kpis.get("hipertensos", 0),
        "diabeticos": kpis.get("diabeticos", 0),
        "fumadores": kpis.get("fumadores", 0),
        "riesgo_promedio": kpis.get("riesgo_promedio", 0),
    }


def distribucion_por_riesgo() -> Dict[str, Any]:
    qs = Patient.objects.all()
    counts = qs.values_list("riesgo_enfermedad", flat=True)
    # Asegurar orden fijo
    order = ["Crítico", "Alto", "Medio", "Bajo"]
    mapping = {k: 0 for k in order}
    for r in counts:
        if r in mapping:
            mapping[r] += 1
    return {"labels": ["Críticos", "Altos", "Medios", "Bajos"], "data": [mapping["Crítico"], mapping["Alto"], mapping["Medio"], mapping["Bajo"]]}


def distribucion_por_sexo() -> Dict[str, Any]:
    qs = Patient.objects.all()
    mapping = {"Masculino": 0, "Femenino": 0, "Desconocido": 0}
    for sexo in qs.values_list("sexo", flat=True):
        if sexo in mapping:
            mapping[sexo] += 1
    labels = ["Masculino", "Femenino", "Desconocido"]
    data = [mapping[l] for l in labels]
    return {"labels": labels, "data": data}


def distribucion_por_diagnostico(top_n: int = 8) -> Dict[str, Any]:
    qs = (
        Patient.objects.values("diagnostico_preliminar")
        .annotate(count=Count("id_paciente"))
        .order_by("-count")[:top_n]
    )
    labels = [row["diagnostico_preliminar"] for row in qs]
    data = [row["count"] for row in qs]
    return {"labels": labels, "data": data}


def segmentaciones_para_graficas() -> Dict[str, Any]:
    """Barras por buckets (edad/IMC) y otros."""
    seg = segmentaciones()

    return {
        "edad_buckets": {
            "labels": list(seg.get("por_edad", {}).keys()),
            "data": list(seg.get("por_edad", {}).values()),
        },
        "imc_buckets": {
            "labels": list(seg.get("por_imc", {}).keys()),
            "data": list(seg.get("por_imc", {}).values()),
        },
    }


def tendencias_por_fecha(bucket: str = "day", limit: int = 14) -> Dict[str, Any]:
    """Tendencias con fuente real.

    Retorna conteo por fecha_consulta para pacientes.
    """
    qs = Patient.objects.all().order_by("-fecha_consulta")[:5000]
    # Agregar in-memory para no depender de DB-specific trunc
    buckets: Dict[str, int] = {}
    for p in qs:
        dt = p.fecha_consulta
        if dt is None:
            continue
        if bucket == "week":
            key = dt.strftime("%Y-W%W")
        else:
            key = dt.isoformat()
        buckets[key] = buckets.get(key, 0) + 1

    # Ordenar por fecha (string ISO o week-sort)
    items = list(buckets.items())
    # Heurística: ISO date lexicographically sorts
    items.sort(key=lambda x: x[0])

    items = items[-limit:]
    labels = [k for k, _ in items]
    data = [v for _, v in items]
    return {"labels": labels, "data": data}


def heatmap_clinico_risk() -> Dict[str, Any]:
    """Heatmap clínico simple: relación discretizada presión sistólica vs glucosa.

    Implementación sin librerías extra: devolvemos matriz (labels x labels x values).
    """
    qs = Patient.objects.all().only(
        "presion_sistolica",
        "glucosa",
        "id_paciente",
    )

    # Discretización
    sist_bins = [(0, 129), (130, 139), (140, 179), (180, 10000)]
    gluc_bins = [(0, 125), (126, 199), (200, 299), (300, 10000)]

    matrix: List[List[int]] = [[0 for _ in gluc_bins] for __ in sist_bins]

    def bin_index(val: float, bins: List[tuple[int, int]]) -> int | None:
        for i, (lo, hi) in enumerate(bins):
            if lo <= val <= hi:
                return i
        return None

    for p in qs:
        i = bin_index(float(p.presion_sistolica or 0), sist_bins)
        j = bin_index(float(p.glucosa or 0), gluc_bins)
        if i is not None and j is not None:
            matrix[i][j] += 1

    sist_labels = ["<130", "130-139", "140-179", ">=180"]
    gluc_labels = ["<126", "126-199", "200-299", ">=300"]

    return {"sist_labels": sist_labels, "gluc_labels": gluc_labels, "matrix": matrix}


def etl_history_summary(limit: int = 10) -> Dict[str, Any]:
    runs = ETLRun.objects.all().order_by("-started_at")[:limit]
    labels = [r.started_at.date().isoformat() for r in runs]
    data = [int(r.records_processed) for r in runs]
    statuses = [r.status for r in runs]
    return {"labels": labels, "data": data, "statuses": statuses}


def predicciones_disponibles() -> Dict[str, Any]:
    """Predicciones bajo demanda (no persistimos en BD aún).

    Para evitar hardcode, calculamos para los primeros N pacientes.
    """
    pacientes = list(Patient.objects.all().order_by("-fecha_consulta")[:50])
    out: List[Dict[str, Any]] = []
    for p in pacientes:
        try:
            risk_label, confidence, _ = predict_risk(
                {
                    "edad": p.edad,
                    "imc": p.imc,
                    "presion_sistolica": p.presion_sistolica,
                    "presion_diastolica": p.presion_diastolica,
                    "glucosa": p.glucosa,
                    "colesterol": p.colesterol,
                }
            )
            out.append(
                {
                    "id_paciente": p.id_paciente,
                    "riesgo_enfermedad": str(risk_label),
                    "confidence": confidence,
                }
            )
        except Exception:
            # Si no existe modelo, retornamos vacío; frontend mostrará 0.
            continue

    return {"count": len(out), "items": out}

