from django.urls import path

from apps.dashboard.views import charts_api, dashboard_view, kpis_api, trends_api

urlpatterns = [
    path("", dashboard_view, name="dashboard_home"),
    path("kpis/", kpis_api, name="dashboard_kpis"),
    path("charts/", charts_api, name="dashboard_charts"),
    path("trends/", trends_api, name="dashboard_trends"),
]


