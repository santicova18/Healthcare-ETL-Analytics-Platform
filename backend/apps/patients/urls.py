from django.urls import path

from apps.patients.views import pacientes_create, pacientes_delete, pacientes_list, pacientes_update

urlpatterns = [
    path("", pacientes_list, name="pacientes_list"),
    path("create/", pacientes_create, name="pacientes_create"),
    path("<int:id_paciente>/update/", pacientes_update, name="pacientes_update"),
    path("<int:id_paciente>/delete/", pacientes_delete, name="pacientes_delete"),
]

