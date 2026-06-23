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
        except Exception:
            # Limpiar archivo temporal si falla la escritura
            try:
                os.unlink(tmp.name)
            except OSError:
                pass
            return None, "Error al guardar el archivo subido."
        finally:
            tmp.close()

    # Si no hay upload, buscar file_path en payload JSON o usar dataset por defecto
    default_dataset = settings.BASE_DIR.parent / "dataset" / "dataset_clinico_etl_1800_registros.xlsx"
    file_path = payload.get("file_path", str(default_dataset))
    if not os.path.exists(file_path):
        return None, f"Archivo no encontrado: {file_path}"
    return file_path, None


@login_required
@role_required("Administrador", "Analista")
@require_http_methods(["POST"])
def etl_run(request):
    """POST /api/etl/run/

    Ejecuta ETL cargando el dataset y persistiendo pacientes.
    Detecta datasets duplicados por hash SHA256 y pacientes duplicados por id_paciente.

    Input:
      - multipart: file (CSV/XLSX)
      - JSON optional: file_path (ruta local en servidor)

    Output (dataset nuevo):
      { "processed": N, "inserted": N, "duplicates": N, "dataset_duplicate": false, "ok": true, ... }

    Output (dataset ya procesado):
      { "success": false, "reason": "dataset_already_processed" }
    """

    payload: Dict[str, Any] = {}
    content_type = request.content_type or ""
    # Solo intentar parsear JSON si el content-type es application/json
    # IMPORTANTE: content_type se verifica PRIMERO para evitar RawPostDataException
    # en requests multipart (cuyo body ya fue consumido por CSRF middleware).
    if "application/json" in content_type and request.body:
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return _json_error("payload JSON inválido")

    file_path, upload_error = _resolve_file_path(request, payload)
    if upload_error:
        return _json_error(upload_error, status=400)

    temp_upload = request.FILES.get("file") is not None
    original_filename = request.FILES.get("file").name if request.FILES.get("file") else None

    start = time.time()

    try:
        if not os.path.exists(file_path):
            return _json_error("file_path no existe en el servidor", status=400)

        result = process_clinical_dataset(file_path, original_filename=original_filename)
        elapsed = round(time.time() - start, 3)

        # Dataset duplicado (Nivel 1)
        if isinstance(result, dict) and result.get("reason") == "dataset_already_processed":
            return JsonResponse(
                {"success": False, "reason": "dataset_already_processed"},
                status=409,
            )

        # Procesamiento exitoso
        processed = result.get("processed", 0)
        inserted = result.get("inserted", 0)
        duplicates = result.get("duplicates", 0)

        run = ETLRun.objects.create(
            user=request.user,
            records_processed=inserted,
            elapsed_seconds=float(elapsed),
            status=ETLRun.Status.OK,
            message="",
        )

        dup_pct = round(duplicates / processed * 100, 2) if processed else 0.0

        return JsonResponse(
            {
                "ok": True,
                "processed": processed,
                "inserted": inserted,
                "duplicates": duplicates,
                "duplicate_percentage": dup_pct,
                "dataset_duplicate": False,
                "elapsed_seconds": elapsed,
                "etl_run_id": run.id,
            },
            status=200,
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        elapsed = round(time.time() - start, 3)

        run = ETLRun.objects.create(
            user=request.user,
            records_processed=0,
            elapsed_seconds=float(elapsed),
            status=ETLRun.Status.FAIL,
            message=traceback.format_exc(),
        )

        return JsonResponse({"error": "Error ejecutando ETL", "details": str(e)}, status=500)
    finally:
        if temp_upload and file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except OSError:
                pass


