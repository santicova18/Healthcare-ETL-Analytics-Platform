"""Validación ligera para endpoints JSON (sin DRF).

El proyecto usa Django Views (no DRF), pero necesitamos sanitizar inputs.
Esta capa provee utilidades de validación simples.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _to_int(value: Any, *, field: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} debe ser entero")


def _to_float(value: Any, *, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} debe ser numérico")


def _to_bool(value: Any, *, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        raise ValueError(f"{field} es requerido")
    s = str(value).strip().lower()
    if s in {"true", "1", "1.0", "yes", "y"}:
        return True
    if s in {"false", "0", "0.0", "no", "n"}:
        return False
    raise ValueError(f"{field} debe ser booleano")


def _normalize_enum(value: Any, *, field: str, allowed: Iterable[str]) -> str:
    if value is None:
        raise ValueError(f"{field} es requerido")
    s = str(value).strip()
    for a in allowed:
        if s.lower() == a.lower():
            # devolver la opción canónica
            return a
    raise ValueError(f"{field} inválido")


RIESGO_ALLOWED = {"Bajo", "Medio", "Alto", "Crítico"}
SEXO_ALLOWED = {"Masculino", "Femenino", "Desconocido"}
ACTIVIDAD_ALLOWED = {"Baja", "Moderada", "Alta"}
DIAGNOSTICO_ALLOWED = None  # opcional (no validamos estricto)


def validate_patient_payload(payload: Dict[str, Any], *, partial: bool = False) -> Dict[str, Any]:
    """Valida/sanitiza payload para creación/lectura de paciente.

    partial=True permite aceptar solo algunos campos (solo se usa para endpoints de filtro si se necesitara).
    """
    if not isinstance(payload, dict):
        raise ValueError("payload debe ser objeto")

    out: Dict[str, Any] = {}

    def req(field: str) -> Any:
        if field in payload:
            return payload[field]
        if partial:
            return None
        raise ValueError(f"{field} es requerido")

    # Campos requeridos del modelo (para alta/POST; para GET no aplica)
    out["id_paciente"] = _to_int(req("id_paciente"), field="id_paciente")
    out["nombres"] = str(req("nombres")).strip()
    out["apellidos"] = str(req("apellidos")).strip()
    out["edad"] = _to_int(req("edad"), field="edad")

    sexo = req("sexo")
    if sexo is None and not partial:
        raise ValueError("sexo es requerido")
    if sexo is not None:
        sexo_norm = str(sexo).strip().lower()
        if sexo_norm in {"m", "masculino"}:
            out["sexo"] = "Masculino"
        elif sexo_norm in {"f", "femenino"}:
            out["sexo"] = "Femenino"
        else:
            out["sexo"] = "Desconocido"

    out["peso"] = _to_float(req("peso"), field="peso")
    out["altura"] = _to_float(req("altura"), field="altura")
    # imc puede venir derivado; si no, lo recalculamos con peso/altura
    imc_val = req("imc")
    if imc_val is None:
        out["imc"] = round(out["peso"] / (out["altura"] ** 2), 2)
    else:
        out["imc"] = _to_float(imc_val, field="imc")

    out["presion_sistolica"] = _to_int(req("presion_sistolica"), field="presion_sistolica")
    out["presion_diastolica"] = _to_int(req("presion_diastolica"), field="presion_diastolica")
    out["frecuencia_cardiaca"] = _to_int(req("frecuencia_cardiaca"), field="frecuencia_cardiaca")

    out["glucosa"] = _to_float(req("glucosa"), field="glucosa")
    out["colesterol"] = _to_float(req("colesterol"), field="colesterol")
    out["saturacion_oxigeno"] = _to_float(req("saturacion_oxigeno"), field="saturacion_oxigeno")
    out["temperatura"] = _to_float(req("temperatura"), field="temperatura")

    out["antecedentes_familiares"] = _to_bool(req("antecedentes_familiares"), field="antecedentes_familiares")
    out["fumador"] = _to_bool(req("fumador"), field="fumador")
    out["consumo_alcohol"] = _to_bool(req("consumo_alcohol"), field="consumo_alcohol")

    act = req("actividad_fisica")
    if act is not None:
        act_norm = str(act).strip().lower()
        if act_norm in {"baja", "low"}:
            out["actividad_fisica"] = "Baja"
        elif act_norm in {"alta", "high"}:
            out["actividad_fisica"] = "Alta"
        else:
            out["actividad_fisica"] = "Moderada"

    out["diagnostico_preliminar"] = str(req("diagnostico_preliminar")).strip()
    out["riesgo_enfermedad"] = _normalize_enum(
        req("riesgo_enfermedad"), field="riesgo_enfermedad", allowed=sorted(RIESGO_ALLOWED)
    )

    # fecha_consulta: acepta date o YYYY-MM-DD
    fc = req("fecha_consulta")
    if isinstance(fc, date):
        out["fecha_consulta"] = fc
    else:
        s = str(fc).strip()
        # formato ISO
        out["fecha_consulta"] = date.fromisoformat(s)

    return out


