import os
import sys
import django

# Asegurar que el directorio 'backend' esté en el sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) == 'backend':
    backend_dir = current_dir
else:
    backend_dir = os.path.join(current_dir, 'backend')

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Configurar Django para que este script pueda "ver" el proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Definir la ruta del archivo de dataset de forma absoluta
BASE_DIR = os.path.dirname(backend_dir)
ruta_archivo = os.path.join(BASE_DIR, 'dataset', 'dataset_clinico_etl_1800_registros.xlsx')

print(f"Buscando archivo en: {ruta_archivo}")

# Importar la función
from apps.etl.services import process_clinical_dataset

print(f"Iniciando procesamiento de: {ruta_archivo}")
cantidad = process_clinical_dataset(ruta_archivo)
print(f"Procesado con éxito. Se guardaron {cantidad} pacientes.")