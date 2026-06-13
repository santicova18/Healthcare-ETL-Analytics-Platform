from django.urls import path

from apps.reports.views import export_patients_csv, export_patients_pdf

urlpatterns = [
    path("export/patients/", export_patients_csv, name="export_patients_csv"),
    path("export/patients/pdf/", export_patients_pdf, name="export_patients_pdf"),
]


