from __future__ import annotations

import json
import os
import tempfile
import time
from typing import Any, Dict

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.authentication.rbac import role_required
from apps.etl.services import process_clinical_dataset

from apps.etl.models import ETLRun


def _json_error(message: str, *, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


@login_required
@role_required("Administrador", "Analista")
def etl_page(request):
    """Página /etl/ — ejecución ETL con subida de archivo."""
    return render(request, "etl.html")


def _resolve_file_path(request, payload: Dict[str, Any]) -> tuple[str | None, str | None]:
    """Resuelve ruta del dataset desde upload o JSON file_path."""
    uploaded = request.FILES.get("file")
    if uploaded:
        ext = os.path.splitext(uploaded.name)[1].lower()
        if ext not in {".csv", ".xlsx", ".xls"}:
            return None, "Formato no soportado. Use CSV o XLSX."
        suffix = ".xlsx" if ext == ".xls" else ext
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        try:
            for chunk in uploaded.chunks():
                tmp.write(chunk)
            tmp.flush()
            return tmp.name, None
        finally:
            tmp.close()

    default_dataset = settings.BASE_DIR.parent / "dataset" / "dataset_clinico_etl_1800_registros.xlsx"
    file_path = payload.get("file_path", str(default_dataset))
    return file_path, None


@login_required
@role_required("Administrador", "Analista")
@require_http_methods(["POST"])
def etl_run(request):
    """POST /api/etl/run/

    Ejecuta ETL cargando el dataset y persistiendo pacientes.

    Input:
      - multipart: file (CSV/XLSX)
      - JSON optional: file_path (ruta local en servidor)
    """

    payload: Dict[str, Any] = {}
    if request.body and not request.FILES:
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return _json_error("payload JSON inválido")

    file_path, upload_error = _resolve_file_path(request, payload)
    if upload_error:
        return _json_error(upload_error)

    temp_upload = request.FILES.get("file") is not None

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
        import traceback
        traceback.print_exc()
        elapsed = round(time.time() - start, 3)
        run.status = ETLRun.Status.FAIL 
        run.elapsed_seconds = float(elapsed)
        run.message = traceback.format_exc()
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "elapsed_seconds", "message", "finished_at"])

        return JsonResponse({"error": "Error ejecutando ETL", "details": str(e)}, status=500)
    finally:
        if temp_upload and file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except OSError:
                pass


