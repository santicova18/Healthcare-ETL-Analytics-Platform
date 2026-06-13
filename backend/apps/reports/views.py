import csv
from io import BytesIO, StringIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from apps.patients.models import Patient


try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except Exception:  # pragma: no cover
    reportlab_available = False
else:
    reportlab_available = True


@login_required
def export_patients_csv(request):
    """Exporta pacientes filtrados a CSV.

    Filtros soportados (opcional):
    - riesgo_enfermedad
    """
    qs = Patient.objects.all().order_by("-fecha_consulta")

    riesgo = request.GET.get("riesgo_enfermedad")
    if riesgo:
        qs = qs.filter(riesgo_enfermedad=riesgo)

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
def export_patients_pdf(request):
    """Exporta pacientes filtrados a PDF (reportlab).

    Filtros soportados (opcional):
    - riesgo_enfermedad

    Endpoint:
    - /api/reports/export/patients/pdf/?riesgo_enfermedad=Crítico
    """
    if not reportlab_available:
        return HttpResponse(
            "reportlab no está instalado en el entorno.", status=500
        )

    qs = Patient.objects.all().order_by("-fecha_consulta")
    riesgo = request.GET.get("riesgo_enfermedad")
    if riesgo:
        qs = qs.filter(riesgo_enfermedad=riesgo)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter
    pdf.setTitle("Pacientes - Export")

    # Header
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, height - 50, "Pacientes - Export")

    pdf.setFont("Helvetica", 10)
    y = height - 75
    total = qs.count()
    pdf.drawString(50, y, f"Total: {total}")
    y -= 20

    pdf.setFont("Helvetica", 9)
    # Data rows (simple, sin tablas complejas)
    for p in qs[:200]:  # limit para evitar PDFs gigantes
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

