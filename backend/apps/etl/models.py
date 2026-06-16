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

