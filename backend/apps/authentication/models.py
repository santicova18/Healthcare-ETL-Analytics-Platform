from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "Administrador", "Administrador"
        MEDICO = "Médico", "Médico"
        ANALISTA = "Analista", "Analista"

    role = models.CharField(
        max_length=30,
        choices=Roles.choices,
        default=Roles.ANALISTA,
        help_text="Rol del usuario para RBAC.",
    )

