import hashlib
import os
import tempfile
from unittest.mock import patch, MagicMock

import pandas as pd
from django.test import TestCase

from apps.etl.models import ETLHistory
from apps.etl.services import _compute_file_hash, process_clinical_dataset
from apps.patients.models import Patient


class ComputeFileHashTest(TestCase):
    def test_returns_sha256_hexdigest(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
            f.write(b"contenido de prueba")
            tmp = f.name
        try:
            expected = hashlib.sha256(b"contenido de prueba").hexdigest()
            self.assertEqual(_compute_file_hash(tmp), expected)
        finally:
            os.unlink(tmp)

    def test_different_files_different_hashes(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f1:
            f1.write(b"archivo a")
            name1 = f1.name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f2:
            f2.write(b"archivo b")
            name2 = f2.name
        try:
            self.assertNotEqual(_compute_file_hash(name1), _compute_file_hash(name2))
        finally:
            os.unlink(name1)
            os.unlink(name2)


class Nivel1DatasetDuplicateDetectionTest(TestCase):
    def test_returns_dataset_already_processed_when_hash_exists(self):
        ETLHistory.objects.create(
            file_hash="a" * 64,
            file_name="previo.csv",
            records_processed=10,
            records_inserted=8,
            records_duplicates=2,
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
            f.write(b"id_paciente,nombres\n1,Test")
            tmp = f.name
        try:
            file_hash = _compute_file_hash(tmp)
            history_entry_file_hash = "a" * 64
            self.assertNotEqual(file_hash, history_entry_file_hash)

            ETLHistory.objects.create(
                file_hash=file_hash,
                file_name="original.csv",
                records_processed=1,
                records_inserted=1,
                records_duplicates=0,
            )

            result = process_clinical_dataset(tmp)
            self.assertFalse(result.get("success", True))
            self.assertEqual(result.get("reason"), "dataset_already_processed")
        finally:
            os.unlink(tmp)

    def test_new_dataset_returns_ok(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as f:
            f.write("id_paciente,nombres,edad,sexo,peso,altura,imc,presion_sistolica,presion_diastolica,frecuencia_cardiaca,glucosa,colesterol,saturacion_oxigeno,temperatura,antecedentes_familiares,fumador,consumo_alcohol,actividad_fisica,diagnostico_preliminar,riesgo_enfermedad,fecha_consulta\n")
            f.write("1,A,30,M,70,1.7,24.2,120,80,72,95,180,98.0,36.5,False,False,False,Moderada,Paciente Sano,Bajo,2024-01-01\n")
            tmp = f.name
        try:
            result = process_clinical_dataset(tmp)
            self.assertNotIn("success", result)
            self.assertEqual(result.get("dataset_duplicate"), False)
        finally:
            os.unlink(tmp)

    def test_nonexistent_file_returns_zeros(self):
        result = process_clinical_dataset("/no/existe.csv")
        self.assertEqual(result.get("processed"), 0)
        self.assertEqual(result.get("dataset_duplicate"), False)

    def test_duplicate_percentage_in_response(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as f:
            f.write("id_paciente,nombres,edad,sexo,peso,altura,imc,presion_sistolica,presion_diastolica,frecuencia_cardiaca,glucosa,colesterol,saturacion_oxigeno,temperatura,antecedentes_familiares,fumador,consumo_alcohol,actividad_fisica,diagnostico_preliminar,riesgo_enfermedad,fecha_consulta\n")
            f.write("1,A,30,M,70,1.7,24.2,120,80,72,95,180,98.0,36.5,False,False,False,Moderada,Paciente Sano,Bajo,2024-01-01\n")
            tmp = f.name
        try:
            result = process_clinical_dataset(tmp)
            self.assertIn("duplicate_percentage", result)
            self.assertIsInstance(result["duplicate_percentage"], float)
        finally:
            os.unlink(tmp)


class Nivel2PatientDuplicateDetectionTest(TestCase):
    def test_detects_existing_patient_by_id(self):
        Patient.objects.create(
            id_paciente=999,
            nombres="Existente",
            apellidos="Paciente",
            edad=40,
            sexo="Masculino",
            peso=80, altura=1.75, imc=26.1,
            presion_sistolica=130, presion_diastolica=85,
            frecuencia_cardiaca=70, glucosa=100, colesterol=190,
            saturacion_oxigeno=98, temperatura=36.5,
            antecedentes_familiares=False, fumador=False,
            consumo_alcohol=False, actividad_fisica="Moderada",
            diagnostico_preliminar="Paciente Sano",
            riesgo_enfermedad="Bajo", fecha_consulta="2024-01-01",
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as f:
            f.write("id_paciente,nombres,edad,sexo,peso,altura,imc,presion_sistolica,presion_diastolica,frecuencia_cardiaca,glucosa,colesterol,saturacion_oxigeno,temperatura,antecedentes_familiares,fumador,consumo_alcohol,actividad_fisica,diagnostico_preliminar,riesgo_enfermedad,fecha_consulta\n")
            f.write("999,Existente,Paciente,40,M,80,1.75,26.1,130,85,70,100,190,98.0,36.5,False,False,False,Moderada,Paciente Sano,Bajo,2024-01-01\n")
            f.write("1000,Nuevo,Paciente,25,F,60,1.65,22.0,110,70,75,90,170,99.0,36.5,False,False,False,Activa,Paciente Sano,Bajo,2024-01-01\n")
            tmp = f.name
        try:
            result = process_clinical_dataset(tmp)
            self.assertEqual(result["processed"], 2)
            self.assertEqual(result["inserted"], 1)
            self.assertEqual(result["duplicates"], 1)
        finally:
            os.unlink(tmp)
            Patient.objects.filter(id_paciente__in=[999, 1000]).delete()

    def test_intra_file_duplicates_removed(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as f:
            f.write("id_paciente,nombres,edad,sexo,peso,altura,imc,presion_sistolica,presion_diastolica,frecuencia_cardiaca,glucosa,colesterol,saturacion_oxigeno,temperatura,antecedentes_familiares,fumador,consumo_alcohol,actividad_fisica,diagnostico_preliminar,riesgo_enfermedad,fecha_consulta\n")
            f.write("1,A,30,M,70,1.7,24.2,120,80,72,95,180,98.0,36.5,False,False,False,Moderada,Paciente Sano,Bajo,2024-01-01\n")
            f.write("1,A,30,M,70,1.7,24.2,120,80,72,95,180,98.0,36.5,False,False,False,Moderada,Paciente Sano,Bajo,2024-01-01\n")
            f.write("2,B,25,F,60,1.65,22.0,110,70,75,90,170,99.0,36.5,False,False,False,Activa,Paciente Sano,Bajo,2024-01-01\n")
            tmp = f.name
        try:
            result = process_clinical_dataset(tmp)
            self.assertEqual(result["processed"], 2)
            self.assertEqual(result["inserted"], 2)
            self.assertEqual(result["duplicates"], 0)
        finally:
            os.unlink(tmp)
            Patient.objects.filter(id_paciente__in=[1, 2]).delete()


class ViewDuplicateDetectionTest(TestCase):
    def test_view_returns_409_for_dataset_duplicate(self):
        from django.test import RequestFactory
        from django.contrib.auth.models import User, AnonymousUser
        from apps.etl.views import etl_run

        user = User.objects.create_user(username="testuser", password="12345")
        factory = RequestFactory()

        ETLHistory.objects.create(
            file_hash="bb" * 32,
            file_name="fake.csv",
            records_processed=1,
            records_inserted=1,
            records_duplicates=0,
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as f:
            f.write("id_paciente,nombres\n1,Test\n")
            tmp = f.name
        try:
            file_hash = _compute_file_hash(tmp)

            ETLHistory.objects.create(
                file_hash=file_hash,
                file_name="original.csv",
                records_processed=1,
                records_inserted=1,
                records_duplicates=0,
            )

            req = factory.post("/api/etl/run/", {"file_path": tmp})
            req.user = user
            resp = etl_run(req)
            self.assertEqual(resp.status_code, 409)

            data = resp.json()
            self.assertEqual(data.get("reason"), "dataset_already_processed")
            self.assertFalse(data.get("success", True))
        finally:
            os.unlink(tmp)
