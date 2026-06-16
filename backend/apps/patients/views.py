from __future__ import annotations

import json
from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods

from apps.authentication.rbac import role_required
from apps.patients.models import Patient
from apps.patients.serializers import validate_patient_payload


def _json_error(message: str, *, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


def _get_optional_filters(request) -> Dict[str, Any]:
    """Filtros soportados por query params."""
    filters: Dict[str, Any] = {}

    riesgo = request.GET.get("riesgo_enfermedad")
    if riesgo:
        filters["riesgo_enfermedad"] = riesgo

    return filters


@login_required
@role_required("Administrador", "Médico", "Analista")
def patients_page(request):
    """Página /patients/ — lista y alta vía fetch a /api/patients/."""
    return render(request, "patients.html", {"user_role": getattr(request.user, "role", "")})


@login_required
@role_required("Administrador", "Médico", "Analista")
@require_GET
def pacientes_list(request):
    """GET /api/pacientes/

    Read-only clinical for Médico/Analista, total access for Administrador.
    """
    filters = _get_optional_filters(request)

    qs = Patient.objects.all().order_by("-fecha_consulta")
    if filters:
        qs = qs.filter(**filters)

    # Respuesta consistente (JSON)
    data = []
    for p in qs[:500]:  # límite preventivo
        data.append(
            {
                "id_paciente": p.id_paciente,
                "nombres": p.nombres,
                "apellidos": p.apellidos,
                "edad": p.edad,
                "sexo": p.sexo,
                "imc": p.imc,
                "riesgo_enfermedad": p.riesgo_enfermedad,
                "fecha_consulta": p.fecha_consulta,
                "presion_sistolica": p.presion_sistolica,
                "presion_diastolica": p.presion_diastolica,
                "glucosa": p.glucosa,
                "diagnostico_preliminar": p.diagnostico_preliminar,
            }
        )

    return JsonResponse({"count": qs.count(), "results": data})


@login_required
@role_required("Administrador", "Médico")
@require_http_methods(["POST"])
def pacientes_create(request):
    """POST /api/patients/create/ (Administrador, Médico)"""
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return _json_error("payload JSON inválido")

    try:
        clean = validate_patient_payload(payload, partial=False)
    except ValueError as e:
        return _json_error(str(e))

    # Guardar
    Patient.objects.update_or_create(id_paciente=clean["id_paciente"], defaults=clean)
    return JsonResponse({"ok": True, "id_paciente": clean["id_paciente"]}, status=201)


def _patient_to_dict(p: Patient) -> Dict[str, Any]:
    return {
        "id_paciente": p.id_paciente,
        "nombres": p.nombres,
        "apellidos": p.apellidos,
        "edad": p.edad,
        "sexo": p.sexo,
        "peso": p.peso,
        "altura": p.altura,
        "imc": p.imc,
        "presion_sistolica": p.presion_sistolica,
        "presion_diastolica": p.presion_diastolica,
        "frecuencia_cardiaca": p.frecuencia_cardiaca,
        "glucosa": p.glucosa,
        "colesterol": p.colesterol,
        "saturacion_oxigeno": p.saturacion_oxigeno,
        "temperatura": p.temperatura,
        "antecedentes_familiares": p.antecedentes_familiares,
        "fumador": p.fumador,
        "consumo_alcohol": p.consumo_alcohol,
        "actividad_fisica": p.actividad_fisica,
        "diagnostico_preliminar": p.diagnostico_preliminar,
        "riesgo_enfermedad": p.riesgo_enfermedad,
        "fecha_consulta": p.fecha_consulta.isoformat(),
    }


@login_required
@role_required("Administrador", "Médico")
@require_http_methods(["POST"])
def pacientes_update(request, id_paciente: int):
    """POST /api/patients/<id>/update/ (Administrador, Médico)"""
    patient = Patient.objects.filter(id_paciente=id_paciente).first()
    if patient is None:
        return _json_error(f"Paciente no encontrado: {id_paciente}", status=404)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return _json_error("payload JSON inválido")

    merged = _patient_to_dict(patient)
    merged.update(payload)
    merged["id_paciente"] = id_paciente

    try:
        clean = validate_patient_payload(merged, partial=False)
    except ValueError as e:
        return _json_error(str(e))

    for field, value in clean.items():
        setattr(patient, field, value)
    patient.save()
    return JsonResponse({"ok": True, "id_paciente": id_paciente})


@login_required
@role_required("Administrador")
@require_http_methods(["POST"])
def pacientes_delete(request, id_paciente: int):
    """POST /api/patients/<id>/delete/ (solo Administrador)"""
    deleted, _ = Patient.objects.filter(id_paciente=id_paciente).delete()
    if not deleted:
        return _json_error(f"Paciente no encontrado: {id_paciente}", status=404)
    return JsonResponse({"ok": True, "id_paciente": id_paciente})

