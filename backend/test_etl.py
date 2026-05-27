import os
import sys
import django

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# 2. Ahora sí, configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Construimos la ruta uniendo las carpetas de forma segura
ruta_archivo = os.path.join(BASE_DIR, 'dataset', 'dataset_clinico_etl_1800_registros.xlsx')

print(f"Buscando archivo en: {ruta_archivo}")

# 1. Configurar Django para que este script pueda "ver" el proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# 2. Importar la función
from apps.etl.services import process_clinical_dataset

# 3. AQUÍ es donde le pasas la ruta
ruta_archivo = "./dataset/dataset_clinico_etl_1800_registros.xlsx"


print(f"Iniciando procesamiento de: {ruta_archivo}")
cantidad = process_clinical_dataset(ruta_archivo)
print(f"Procesado con éxito. Se guardaron {cantidad} pacientes.")