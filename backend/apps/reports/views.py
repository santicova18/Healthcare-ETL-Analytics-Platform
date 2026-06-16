import csv
from io import BytesIO, StringIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from apps.authentication.rbac import role_required
from apps.patients.models import Patient

from .services import parse_patient_filters, filtered_patients

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except Exception:  # pragma: no cover
    reportlab_available = False
else:
    reportlab_available = True

try:
    import openpyxl  # noqa: F401
    from openpyxl.utils.dataframe import dataframe_to_rows
except Exception:  # pragma: no cover
    openpyxl_available = False
else:
    openpyxl_available = True

import datetime


@login_required
@role_required('Administrador', 'Médico', 'Analista')
def export_patients_csv(request):
    """Exporta pacientes filtrados a CSV.

    Filtros soportados (opcional):
    - riesgo_enfermedad
    """
    filters = parse_patient_filters(request)
    qs = filtered_patients(filters)

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "id_paciente",
            "nombres",
            "apellidos",
            "edad",
            "sexo",
            "imc",
            "riesgo_enfermedad",
            "fecha_consulta",
        ]
    )

    for p in qs:
        writer.writerow(
            [
                p.id_paciente,
                p.nombres,
                p.apellidos,
                p.edad,
                p.sexo,
                p.imc,
                p.riesgo_enfermedad,
                p.fecha_consulta,
            ]
        )

    response = HttpResponse(output.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="pacientes.csv"'
    return response


@login_required
@role_required('Administrador', 'Médico', 'Analista')
def export_patients_pdf(request):
    """Exporta pacientes filtrados a PDF (reportlab).

    Filtros soportados (opcional):
    - riesgo_enfermedad
    """
    if not reportlab_available:
        return HttpResponse("reportlab no está instalado en el entorno.", status=500)

    filters = parse_patient_filters(request)
    qs = filtered_patients(filters)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter
    pdf.setTitle("Pacientes - Export")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, height - 50, "Pacientes - Export")

    pdf.setFont("Helvetica", 10)
    y = height - 75
    total = qs.count()
    pdf.drawString(50, y, f"Total: {total}")
    y -= 20

    pdf.setFont("Helvetica", 9)
    for p in qs[:200]:
        line = (
            f"#{p.id_paciente} | {p.nombres} {p.apellidos} | "
            f"Edad: {p.edad} | IMC: {p.imc} | Riesgo: {p.riesgo_enfermedad} | "
            f"Fecha: {p.fecha_consulta}"
        )
        pdf.drawString(50, y, line[:120])
        y -= 12
        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 9)

    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="pacientes.pdf"'
    return response


@login_required
@role_required('Administrador', 'Médico', 'Analista')
def export_patients_excel(request):
    """Exporta Excel (.xlsx) con 5 hojas usando la MISMA fuente base que CSV/PDF.

    Requiere openpyxl.

    Filtros soportados (opcional):
    - riesgo_enfermedad
    """
    if not openpyxl_available:
        return HttpResponse("openpyxl no está instalado en el entorno.", status=500)

    filters = parse_patient_filters(request)
    qs = filtered_patients(filters)

    # Import local para no romper import si no se usa.
    from openpyxl import Workbook

    wb = Workbook()

    # Hoja 1: Pacientes
    ws_pac = wb.active
    ws_pac.title = "Pacientes"
    headers = [
        "id_paciente",
        "nombres",
        "apellidos",
        "edad",
        "sexo",
        "imc",
        "riesgo_enfermedad",
        "fecha_consulta",
    ]
    ws_pac.append(headers)
    for p in qs:
        ws_pac.append(
            [
                p.id_paciente,
                p.nombres,
                p.apellidos,
                p.edad,
                p.sexo,
                p.imc,
                p.riesgo_enfermedad,
                p.fecha_consulta,
            ]
        )

    # Hoja 2: KPIs (recalculados desde la misma query base)
    ws_kpi = wb.create_sheet("KPIs")
    ws_kpi.append(["kpi", "valor"])
    # KPI simples para evitar dependencia en analytics.services
    risco_count = {
        "Bajo": qs.filter(riesgo_enfermedad="Bajo").count(),
        "Medio": qs.filter(riesgo_enfermedad="Medio").count(),
        "Alto": qs.filter(riesgo_enfermedad="Alto").count(),
        "Crítico": qs.filter(riesgo_enfermedad="Crítico").count(),
    }
    ws_kpi.append(["total_pacientes", qs.count()])
    for k, v in risco_count.items():
        ws_kpi.append([f"pacientes_{k.lower()}", v])

    # Hoja 3: Segmentaciones (básico por edad bucket e IMC bucket)
    ws_seg = wb.create_sheet("Segmentaciones")
    ws_seg.append(["segmento", "valor"])
    # edad buckets
    def age_bucket(age: int) -> str:
        if age < 18:
            return "<18"
        if age < 35:
            return "18-34"
        if age < 50:
            return "35-49"
        if age < 65:
            return "50-64"
        return "65+"

    age_counts = {}
    for age in qs.values_list("edad", flat=True):
        key = age_bucket(int(age))
        age_counts[key] = age_counts.get(key, 0) + 1

    for k, v in sorted(age_counts.items()):
        ws_seg.append([f"edad:{k}", v])

    # Hoja 4: Predicciones (no persistidas)
    ws_pred = wb.create_sheet("Predicciones")
    ws_pred.append(["id_paciente", "riesgo_enfermedad", "confidence"])
    # Para no romper si el modelo no existe, se llenan solo si hay.
    from apps.ml.predict import predict_risk

    for p in qs.order_by("-fecha_consulta")[:50]:
        try:
            risk_label, confidence, _ = predict_risk(
                {
                    "edad": p.edad,
                    "imc": p.imc,
                    "presion_sistolica": p.presion_sistolica,
                    "presion_diastolica": p.presion_diastolica,
                    "glucosa": p.glucosa,
                    "colesterol": p.colesterol,
                }
            )
            ws_pred.append([p.id_paciente, str(risk_label), float(confidence)])
        except Exception:
            continue

    # Hoja 5: Historial ETL
    from apps.etl.models import ETLRun

    ws_etl = wb.create_sheet("Historial ETL")
    ws_etl.append(["started_at", "records_processed", "status"])
    for r in ETLRun.objects.all().order_by("-started_at")[:50]:
        ws_etl.append([r.started_at.isoformat(), int(r.records_processed), r.status])

    # Metadata
    ws_meta = wb.create_sheet("Meta")
    ws_meta.append(["generated_at", datetime.datetime.now().isoformat()])
    ws_meta.append(["filter_riesgo_enfermedad", filters.riesgo_enfermedad or "(none)"])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="healthanalytics_report.xlsx"'
    return response

