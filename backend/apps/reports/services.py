from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from django.db.models import QuerySet

from apps.patients.models import Patient


RISK_ALLOWED = {"Bajo", "Medio", "Alto", "Crítico"}


@dataclass(frozen=True)
class PatientFilters:
    riesgo_enfermedad: Optional[str] = None


def parse_patient_filters(request) -> PatientFilters:
    riesgo = request.GET.get("riesgo_enfermedad")
    if riesgo is not None and riesgo != "":
        riesgo = str(riesgo).strip()
        if riesgo not in RISK_ALLOWED:
            # Mantener tolerancia: si viene inválido, no filtramos
            riesgo = None
    else:
        riesgo = None

    return PatientFilters(riesgo_enfermedad=riesgo)


def filtered_patients(filters: PatientFilters) -> QuerySet[Patient]:
    qs = Patient.objects.all().order_by("-fecha_consulta")
    if filters.riesgo_enfermedad:
        qs = qs.filter(riesgo_enfermedad=filters.riesgo_enfermedad)
    return qs


def patient_filters_to_kpis_context(filters: PatientFilters) -> Dict[str, Any]:
    """Contexto mínimo para Excel y validación.

    Nota: no recalcula KPIs; el objetivo aquí es que todas las exportaciones usen
    exactamente la misma fuente/consulta base para pacientes.
    """
    qs = filtered_patients(filters)
    return {"total_pacientes": qs.count()}

