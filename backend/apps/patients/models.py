from django.db import models

class Patient(models.Model):
    # Identificación
    id_paciente = models.IntegerField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=10)
    
    # Datos clínicos básicos
    peso = models.FloatField()
    altura = models.FloatField()
    imc = models.FloatField(db_column='IMC')
    
    # Signos vitales
    presion_sistolica = models.IntegerField()
    presion_diastolica = models.IntegerField()
    frecuencia_cardiaca = models.IntegerField()
    glucosa = models.FloatField()
    colesterol = models.FloatField()
    saturacion_oxigeno = models.FloatField()
    temperatura = models.FloatField()
    
    # Antecedentes y hábitos
    antecedentes_familiares = models.BooleanField()
    fumador = models.BooleanField()
    consumo_alcohol = models.BooleanField()
    actividad_fisica = models.CharField(max_length=50)
    
    # Diagnóstico y Riesgo
    diagnostico_preliminar = models.CharField(max_length=100)
    riesgo_enfermedad = models.CharField(max_length=50)
    fecha_consulta = models.DateField()

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        db_table = 'patients_patient' # Nombre explícito en la DB

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.riesgo_enfermedad}"
