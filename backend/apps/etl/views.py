from __future__ import annotations

import json
import os
import time
from typing import Any, Dict

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.authentication.rbac import role_required
from apps.etl.services import process_clinical_dataset

from apps.etl.models import ETLRun


def _json_error(message: str, *, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


@login_required
@role_required("Administrador", "Analista")
@require_http_methods(["POST"])
def etl_run(request):
    """POST /api/etl/run/

    Ejecuta ETL cargando el dataset y persistiendo pacientes.

    Input (JSON optional):
      - file_path: ruta local al .xlsx/.csv dentro del servidor (opcional)

    Por defecto usa dataset/dataset_clinico_etl_1800_registros.xlsx
    """

    payload: Dict[str, Any] = {}
    if request.body:
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return _json_error("payload JSON inválido")

    default_dataset = settings.BASE_DIR.parent / "dataset" / "dataset_clinico_etl_1800_registros.xlsx"
    file_path = payload.get("file_path", str(default_dataset))

    start = time.time()

    run = ETLRun.objects.create(
        user=request.user,
        records_processed=0,
        elapsed_seconds=0.0,
        status=ETLRun.Status.OK,
        message="",
    )

    try:
        if not os.path.exists(file_path):
            run.status = ETLRun.Status.FAIL
            run.message = "file_path no existe en el servidor"
            run.finished_at = timezone.now()
            run.save(update_fields=["status", "message", "finished_at"])
            return _json_error("file_path no existe en el servidor", status=400)

        created = process_clinical_dataset(file_path)
        elapsed = round(time.time() - start, 3)

        run.records_processed = int(created)
        run.elapsed_seconds = float(elapsed)
        run.status = ETLRun.Status.OK
        run.message = ""
        run.finished_at = timezone.now()
        run.save(
            update_fields=[
                "records_processed",
                "elapsed_seconds",
                "status",
                "message",
                "finished_at",
            ]
        )

        return JsonResponse(
            {
                "ok": True,
                "records_created": created,
                "elapsed_seconds": elapsed,
                "etl_run_id": run.id,
            },
            status=200,
        )
    except Exception as e:
        elapsed = round(time.time() - start, 3)
        run.status = ETLRun.Status.FAIL 
        run.elapsed_seconds = float(elapsed)
        run.message = str(e)
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "elapsed_seconds", "message", "finished_at"])

        return JsonResponse({"error": "Error ejecutando ETL", "details": str(e)}, status=500)


