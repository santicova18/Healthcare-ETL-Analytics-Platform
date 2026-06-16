from django.urls import path

from apps.etl.views import etl_run

urlpatterns = [
    path("run/", etl_run, name="etl_run"),
]

