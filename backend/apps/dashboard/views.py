from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from apps.authentication.rbac import role_required
from apps.dashboard.services import (
    dashboard_kpis,
    distribucion_por_diagnostico,
    distribucion_por_riesgo,
    distribucion_por_sexo,
    etl_history_summary,
    heatmap_clinico_risk,
    predicciones_disponibles,
    segmentaciones_para_graficas,
    tendencias_por_fecha,
)


@login_required
@role_required("Administrador", "Médico", "Analista")
@require_GET
def kpis_api(request):
    """GET /api/dashboard/kpis/"""
    return JsonResponse(dashboard_kpis())


@login_required
@role_required("Administrador", "Médico", "Analista")
@require_GET
def charts_api(request):
    """GET /api/dashboard/charts/"""
    seg = segmentaciones_para_graficas()

    return JsonResponse(
        {
            "distribucion_riesgo": distribucion_por_riesgo(),
            "distribucion_sexo": distribucion_por_sexo(),
            "distribucion_diagnostico": distribucion_por_diagnostico(),
            "edad_buckets": seg["edad_buckets"],
            "imc_buckets": seg["imc_buckets"],
            "heatmap_clinico": heatmap_clinico_risk(),
            "predicciones": predicciones_disponibles(),
        }
    )


@login_required
@role_required("Administrador", "Médico", "Analista")
@require_GET
def trends_api(request):
    """GET /api/dashboard/trends/"""
    return JsonResponse(
        {
            "tendencias_pacientes": tendencias_por_fecha(),
            "etl_history": etl_history_summary(),
        }
    )


@login_required
@role_required("Administrador", "Médico", "Analista")
def dashboard_view(request):
    # Template ahora consume datos desde APIs (fetch).
    return render(request, "dashboard.html", {})

