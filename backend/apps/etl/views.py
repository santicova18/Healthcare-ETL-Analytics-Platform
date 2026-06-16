from __future__ import annotations

import json
import os
import time
from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

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

    file_path = payload.get(
        "file_path",
        "dataset/dataset_clinico_etl_1800_registros.xlsx",
    )

    start = time.time()

    etl_run = ETLRun.objects.create(
        user=request.user,
        records_processed=0,
        elapsed_seconds=0.0,
        status=ETLRun.Status.OK,
        message="",
    )

    try:
        if not os.path.exists(file_path):
            etl_run.status = ETLRun.Status.FAIL
            etl_run.message = "file_path no existe en el servidor"
            etl_run.finished_at = None  # se llenará en save más abajo
            etl_run.save(update_fields=["status", "message"])
            return _json_error("file_path no existe en el servidor", status=400)

        created = process_clinical_dataset(file_path)
        elapsed = round(time.time() - start, 3)

        etl_run.records_processed = int(created)
        etl_run.elapsed_seconds = float(elapsed)
        etl_run.status = ETLRun.Status.OK
        etl_run.message = ""
        etl_run.finished_at = None  # se llenará con update
        etl_run.save(update_fields=[
            "records_processed",
            "elapsed_seconds",
            "status",
            "message",
            "finished_at",
        ])

        return JsonResponse(
            {
                "ok": True,
                "records_created": created,
                "elapsed_seconds": elapsed,
                "etl_run_id": etl_run.id,
            },
            status=200,
        )
    except Exception as e:
        elapsed = round(time.time() - start, 3)
        etl_run.status = ETLRun.Status.FAIL
        etl_run.elapsed_seconds = float(elapsed)
        etl_run.message = str(e)
        etl_run.finished_at = None
        etl_run.save(update_fields=["status", "elapsed_seconds", "message", "finished_at"])

        return JsonResponse({"error": "Error ejecutando ETL", "details": str(e)}, status=500)


