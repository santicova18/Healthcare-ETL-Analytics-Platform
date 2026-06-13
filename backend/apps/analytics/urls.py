from django.urls import path

from apps.analytics.views import risk_summary

urlpatterns = [
    path("risk-summary/", risk_summary, name="risk_summary"),
]

