from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "id_paciente",
        "nombres",
        "apellidos",
        "edad",
        "sexo",
        "riesgo_enfermedad",
        "fecha_consulta",
    )
    list_filter = ("riesgo_enfermedad", "sexo", "fumador")
    search_fields = ("nombres", "apellidos", "id_paciente")
