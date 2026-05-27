import os
import pandas as pd
from apps.patients.models import Patient

def process_clinical_dataset(file_path):
    # 1. Validación de existencia
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No existe el archivo de dataset: {file_path}")

    # 2. Lectura eficiente
    if file_path.lower().endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)

    # 3. Normalización de columnas
    df.columns = df.columns.str.lower().str.replace('ó', 'o').str.replace('í', 'i').str.replace('á', 'a').str.replace('é', 'e').str.replace('ú', 'u')
    
    # 4. LIMPIEZA ESTRICTA (Dropeo de registros)
    # Definimos las columnas que son indispensables para un diagnóstico clínico
    columnas_criticas = ['id_paciente', 'peso', 'altura', 'imc', 'presion_sistolica', 'presion_diastolica', 'glucosa']
    
    # Eliminamos filas donde falte CUALQUIERA de las columnas críticas
    df_limpio = df.dropna(subset=columnas_criticas)
    
    # Log de integridad
    registros_eliminados = len(df) - len(df_limpio)
    print(f"--- ETL Report ---")
    print(f"Registros totales: {len(df)}")
    print(f"Registros eliminados por datos incompletos: {registros_eliminados}")
    print(f"Registros limpios para procesar: {len(df_limpio)}")

    # 5. Normalización de valores
    df_limpio['sexo'] = df_limpio['sexo'].replace({'m': 'Masculino', 'M': 'Masculino', 'f': 'Femenino', 'F': 'Femenino'})
    
    patients_to_create = []
    
    # 6. Iteración y creación de objetos
    for _, row in df_limpio.iterrows():
        try:
            patient = Patient(
                id_paciente=int(row['id_paciente']),
                nombres=str(row.get('nombres', 'N/A')),
                apellidos=str(row.get('apellidos', 'N/A')),
                edad=int(row['edad']),
                sexo=str(row['sexo']),
                peso=float(row['peso']),
                altura=float(row['altura']),
                imc=float(row['imc']),
                presion_sistolica=int(row['presion_sistolica']),
                presion_diastolica=int(row['presion_diastolica']),
                frecuencia_cardiaca=int(row['frecuencia_cardiaca']),
                glucosa=float(row['glucosa']),
                colesterol=float(row['colesterol']),
                saturacion_oxigeno=float(row['saturacion_oxigeno']),
                temperatura=float(row['temperatura']),
                antecedentes_familiares=bool(row['antecedentes_familiares']),
                fumador=bool(row['fumador']),
                consumo_alcohol=bool(row['consumo_alcohol']),
                actividad_fisica=str(row['actividad_fisica']),
                diagnostico_preliminar=str(row['diagnostico_preliminar']),
                riesgo_enfermedad=str(row['riesgo_enfermedad']),
                fecha_consulta=pd.to_datetime(row['fecha_consulta']).date()
            )
            patients_to_create.append(patient)
        except Exception as e:
            # Si una fila falla individualmente, no detenemos el proceso, solo logueamos
            print(f"Error procesando paciente ID {row.get('id_paciente')}: {e}")
            continue

    # 7. Inserción masiva
    if patients_to_create:
        Patient.objects.bulk_create(patients_to_create, ignore_conflicts=True)
    
    return len(patients_to_create)