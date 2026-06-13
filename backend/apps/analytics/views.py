from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from apps.patients.models import Patient


@login_required
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

