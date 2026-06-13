from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.patients.models import Patient


@login_required
def dashboard_view(request):
    """Muestra el dashboard.

    Nota: el cálculo del resumen de riesgo vive en apps/analytics (endpoint /risk-summary/).
    Para mantener la página sin JS adicional, también calculamos stats aquí si no están.
    """

    patients = Patient.objects.all().order_by("-fecha_consulta")


    # Resumen de riesgo (por contrato: el cálculo vive en apps/analytics).
    # Para render server-side sin JS, reutilizamos el conteo aquí como fallback.
    # En un siguiente paso, el frontend podría consumir /api/analytics/risk-summary/.
    stats = {
        "criticos": patients.filter(riesgo_enfermedad="Crítico").count(),
        "altos": patients.filter(riesgo_enfermedad="Alto").count(),
        "medios": patients.filter(riesgo_enfermedad="Medio").count(),
        "bajos": patients.filter(riesgo_enfermedad="Bajo").count(),
    }


    return render(
        request,
        "templates/dashboard/index.html",
        {"patients": patients, "stats": stats},
    )

