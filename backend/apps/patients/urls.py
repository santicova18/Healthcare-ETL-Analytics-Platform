from django.urls import path

from apps.patients.views import pacientes_list, pacientes_create

urlpatterns = [
    path("", pacientes_list, name="pacientes_list"),

    path("create/", pacientes_create, name="pacientes_create"),
]

