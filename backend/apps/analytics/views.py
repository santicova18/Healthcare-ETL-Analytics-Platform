from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from apps.authentication.rbac import role_required
from apps.analytics.services import estadisticas_descriptivas, kpis_clinicos, segmentaciones
from apps.patients.models import Patient


@login_required
@role_required('Administrador', 'Médico', 'Analista')
@require_GET
def risk_summary(request):
    """Devuelve un resumen de riesgo (conteos) para consumo por dashboard."""
    patients = Patient.objects.all()

    stats = {
        "criticos": patients.filter(riesgo_enfermedad="Crítico").count(),
        "altos": patients.filter(riesgo_enfermedad="Alto").count(),
        "medios": patients.filter(riesgo_enfermedad="Medio").count(),
        "bajos": patients.filter(riesgo_enfermedad="Bajo").count(),
    }
    return JsonResponse(stats)


@login_required
@role_required('Administrador', 'Médico', 'Analista')
@require_GET
def kpis_clinicos_api(request):
    """GET /api/analytics/kpis-clinicos/"""
    return JsonResponse(kpis_clinicos())


@login_required
@role_required('Administrador', 'Médico', 'Analista')
@require_GET
def stats_descriptivas_api(request):
    """GET /api/analytics/stats-descriptivas/"""
    return JsonResponse(estadisticas_descriptivas())


@login_required
@role_required('Administrador', 'Médico', 'Analista')
@require_GET
def segmentaciones_api(request):
    """GET /api/analytics/segmentaciones/"""
    return JsonResponse(segmentaciones())


