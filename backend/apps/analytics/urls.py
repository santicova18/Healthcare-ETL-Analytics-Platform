from django.urls import path

from apps.analytics.views import (
    kpis_clinicos_api,
    risk_summary,
    segmentaciones_api,
    stats_descriptivas_api,
)

urlpatterns = [
    path("risk-summary/", risk_summary, name="risk_summary"),
    path("kpis-clinicos/", kpis_clinicos_api, name="kpis_clinicos"),
    path("stats-descriptivas/", stats_descriptivas_api, name="stats_descriptivas"),
    path("segmentaciones/", segmentaciones_api, name="segmentaciones"),
]



