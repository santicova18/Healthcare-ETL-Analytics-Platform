from django.conf import settings
from django.db import models


class ETLRun(models.Model):
    """Historial de ejecuciones del endpoint ETL."""

    class Status(models.TextChoices):
        OK = "OK", "OK"
        FAIL = "FAIL", "FAIL"

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="etl_runs",
    )

    records_processed = models.PositiveIntegerField(default=0)
    elapsed_seconds = models.FloatField(default=0.0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OK)
    message = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return f"ETLRun(status={self.status}, records={self.records_processed}, started_at={self.started_at})"


class ETLHistory(models.Model):
    """Historial de datasets procesados por ETL con hash SHA256 para detección de duplicados."""

    file_hash = models.CharField(max_length=64, unique=True, verbose_name="Hash SHA256 del archivo")
    file_name = models.CharField(max_length=255, verbose_name="Nombre del archivo")
    records_processed = models.PositiveIntegerField(default=0, verbose_name="Registros procesados (limpios)")
    records_inserted = models.PositiveIntegerField(default=0, verbose_name="Registros insertados (nuevos)")
    records_duplicates = models.PositiveIntegerField(default=0, verbose_name="Registros duplicados ignorados")
    processed_at = models.DateTimeField(auto_now_add=True, verbose_name="Procesado el")

    class Meta:
        verbose_name = "Historial ETL"
        verbose_name_plural = "Historiales ETL"
        db_table = "etl_history"
        ordering = ["-processed_at"]

    def __str__(self) -> str:
        return f"{self.file_name} ({self.file_hash[:12]}...) - {self.records_inserted} insertados"

