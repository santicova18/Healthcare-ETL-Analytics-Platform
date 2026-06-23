from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from django.db.models import Q

from apps.patients.models import Patient


def _risk_avg(patients: List[Patient]) -> float:
    mapping = {"Bajo": 1, "Medio": 2, "Alto": 3, "Crítico": 4}
    if not patients:
        return 0.0
    total = 0.0
    for p in patients:
        total += float(mapping.get(p.riesgo_enfermedad, 0))
    return total / float(len(patients))


def kpis_clinicos() -> Dict[str, Any]:
    """KPIs clínicos basados 1:1 con el enunciado.

    Hipertensión:
      sistólica > 140 OR diastólica > 90

    Diabetes:
      glucosa > 200

    Crítico:
      sistólica > 180 OR glucosa > 300 OR saturación < 85
    """
    qs = Patient.objects.all()

    hipertensos = qs.filter(Q(presion_sistolica__gt=140) | Q(presion_diastolica__gt=90))
    diabeticos = qs.filter(glucosa__gt=200)

    criticos = qs.filter(
        Q(presion_sistolica__gt=180)
        | Q(glucosa__gt=300)
        | Q(saturacion_oxigeno__lt=85)
    )

    fumadores = qs.filter(fumador=True)

    patients = list(qs.only("riesgo_enfermedad"))

    return {
        "hipertensos": hipertensos.count(),
        "diabeticos": diabeticos.count(),
        "fumadores": fumadores.count(),
        "criticos": criticos.count(),
        "riesgo_promedio": _risk_avg(patients),
        "total_pacientes": qs.count(),
    }


def estadisticas_descriptivas() -> Dict[str, Any]:
    """Media/mediana/moda/desviación estándar sobre variables clínicas principales."""
    qs = Patient.objects.all()

    # Traer columnas relevantes
    data = list(
        qs.values_list(
            "edad",
            "imc",
            "presion_sistolica",
            "presion_diastolica",
            "glucosa",
            "saturacion_oxigeno",
        )
    )
    if not data:
        return {
            "count": 0,
            "media": {},
            "mediana": {},
            "moda": {},
            "desviacion_estandar": {},
        }

    arr = np.array(data, dtype=float)
    # columnas en el orden indicado
    cols = [
        "edad",
        "imc",
        "presion_sistolica",
        "presion_diastolica",
        "glucosa",
        "saturacion_oxigeno",
    ]

    out_media = {}
    out_mediana = {}
    out_moda = {}
    out_std = {}

    for i, c in enumerate(cols):
        col_vals = arr[:, i]
        out_media[c] = float(np.mean(col_vals))
        out_mediana[c] = float(np.median(col_vals))

        # Moda: valor más frecuente (si múltiples, devolver el primero)
        vals_int = np.array(col_vals)
        # redondear a 2 decimales para evitar modos infinitos por floats
        if c in {"imc", "glucosa", "saturacion_oxigeno"}:
            vals_int = np.round(vals_int, 2)
        unique, counts = np.unique(vals_int, return_counts=True)
        moda_val = unique[int(np.argmax(counts))] if len(unique) else None
        out_moda[c] = float(moda_val) if moda_val is not None else None

        out_std[c] = float(np.std(col_vals, ddof=0))

    return {
        "count": len(data),
        "media": out_media,
        "mediana": out_mediana,
        "moda": out_moda,
        "desviacion_estandar": out_std,
    }


def segmentaciones() -> Dict[str, Any]:
    """Segmentaciones por edad, sexo, IMC, diagnóstico y riesgo."""
    qs = Patient.objects.all()

    # Edad: histograma simple por buckets
    edades = list(qs.values_list("edad", flat=True))
    def bucket_age(age: int) -> str:
        if age < 18:
            return "<18"
        if age < 35:
            return "18-34"
        if age < 50:
            return "35-49"
        if age < 65:
            return "50-64"
        return "65+"

    age_counts: Dict[str, int] = {}
    for a in edades:
        key = bucket_age(int(a))
        age_counts[key] = age_counts.get(key, 0) + 1

    # Sexo
    sexo_counts = {
        "Masculino": qs.filter(sexo="Masculino").count(),
        "Femenino": qs.filter(sexo="Femenino").count(),
        "Desconocido": qs.filter(sexo="Desconocido").count(),
    }

    # IMC buckets (OMS simplificado)
    def bucket_imc(imc: float) -> str:
        if imc < 18.5:
            return "Bajo"
        if imc < 25.0:
            return "Normal"
        if imc < 30.0:
            return "Sobrepeso"
        return "Obesidad"

    imc_vals = list(qs.values_list("imc", flat=True))
    imc_counts: Dict[str, int] = {}
    for v in imc_vals:
        key = bucket_imc(float(v))
        imc_counts[key] = imc_counts.get(key, 0) + 1

    # Diagnóstico: por campo `diagnostico_preliminar`
    diagnostico_qs = qs.values_list("diagnostico_preliminar", flat=True)
    diagnostico_counts: Dict[str, int] = {}
    for d in diagnostico_qs:
        diagnostico_counts[str(d)] = diagnostico_counts.get(str(d), 0) + 1

    # Riesgo
    riesgo_counts = {
        "Bajo": qs.filter(riesgo_enfermedad="Bajo").count(),
        "Medio": qs.filter(riesgo_enfermedad="Medio").count(),
        "Alto": qs.filter(riesgo_enfermedad="Alto").count(),
        "Crítico": qs.filter(riesgo_enfermedad="Crítico").count(),
    }

    return {
        "por_edad": age_counts,
        "por_sexo": sexo_counts,
        "por_imc": imc_counts,
        "por_diagnostico": diagnostico_counts,
        "por_riesgo": riesgo_counts,
    }

