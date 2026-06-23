# 📦 MLOps - Control de Versiones de Modelos

## 📋 Estructura de Carpetas

```
apps/ml/
├── logs/
│   ├── model_versions/           ← Histórico de todas las versiones
│   │   ├── v_20260603_143022/    ← Versión 1 (2026-06-03 14:30:22)
│   │   │   ├── risk_model.pkl    ← Modelo entrenado
│   │   │   ├── scaler.pkl        ← Escalador
│   │   │   ├── label_encoder.pkl ← Codificador de etiquetas
│   │   │   ├── metadata.json     ← Metadatos (hiperparámetros, métricas)
│   │   │   ├── confusion_matrix.png
│   │   │   ├── correlation_matrix.png
│   │   │   ├── feature_importance.png
│   │   │   ├── feature_importance.csv
│   │   │   ├── classification_report.txt
│   │   │   └── RESUMEN.txt
│   │   ├── v_20260603_150000/    ← Versión 2
│   │   └── v_TIMESTAMP.../       ← Todas las versiones del modelo
│   ├── training_reports/         ← Reportes consolidados
│   └── metrics/                  ← Métricas agregadas
├── models/                       ← ACTUAL (los archivos que usa predict.py)
│   ├── risk_model.pkl           ← Versión actual
│   ├── scaler.pkl
│   ├── label_encoder.pkl
│   └── confusion_matrix.png
```

---

## 🎯 Por Qué es Importante el Control de Versiones

### Escenarios Reales:

1. **"Mi modelo empezó a fallar"**
   - Puedes volver a la versión anterior: `cp logs/model_versions/v_20260603_143022/* models/`

2. **"Necesito comparar dos entrenamientos"**
   - Lee `logs/model_versions/v1/metadata.json` vs `v2/metadata.json`
   - Compara métricas y hiperparámetros

3. **"Auditoría: ¿qué modelo usamos el 3 de junio?"**
   - Ver todas las versiones con timestamp en el nombre

4. **"Incremento de Críticos mal clasificados"**
   - Analiza `confusion_matrix.png` de cada versión
   - Identifica en qué entrenamiento empezó el problema

---

## 🚀 Cómo Usar

### 1. Re-entrenar el modelo (con versionado automático):

```bash
cd backend
python retrain_model.py
```

**Resultado:**
- Se crea automáticamente una carpeta `v_TIMESTAMP` con todos los artefactos
- Se actualiza `apps/ml/models/` con el nuevo modelo (para que predict.py lo use)
- Se genera un archivo `RESUMEN.txt` con el reporte completo

### 2. Revisar historial de entrenamientos:

```bash
ls -la apps/ml/logs/model_versions/
```

Output:
```
v_20260603_143022/
v_20260603_150000/
v_20260603_151530/
```

### 3. Comparar dos versiones:

```bash
# Ver metadatos de versión 1
cat apps/ml/logs/model_versions/v_20260603_143022/metadata.json

# Ver metadatos de versión 2
cat apps/ml/logs/model_versions/v_20260603_150000/metadata.json

# Comparar métricas
diff <(jq .metrics apps/ml/logs/model_versions/v_20260603_143022/metadata.json) \
     <(jq .metrics apps/ml/logs/model_versions/v_20260603_150000/metadata.json)
```

### 4. Volver a una versión anterior (rollback):

```bash
# Si el modelo actual empieza a fallar y quieres volver a una versión anterior
cp apps/ml/logs/model_versions/v_20260603_143022/*.pkl apps/ml/models/

# Verificar que funciona
python test_predict.py
```

---

## 📊 Contenido de Metadatos (metadata.json)

```json
{
  "version": "v_20260603_143022",
  "timestamp": "2026-06-03T14:30:22.123456",
  "dataset": {
    "total_samples": 1000,
    "train_samples": 800,
    "test_samples": 200,
    "features": ["edad", "imc", "presion_sistolica", ...],
    "classes": ["Bajo", "Medio", "Alto", "Crítico"]
  },
  "class_distribution": {
    "before_smote": {"Bajo": 50, "Medio": 100, "Alto": 200, "Crítico": 650},
    "after_smote": {"Bajo": 650, "Medio": 650, "Alto": 650, "Crítico": 650}
  },
  "hyperparameters": {
    "n_estimators": 150,
    "max_depth": 15,
    "class_weight": "balanced"
  },
  "metrics": {
    "accuracy_train": 0.9423,
    "accuracy_test": 0.8956,
    "precision_per_class": {
      "Bajo": 0.92,
      "Medio": 0.85,
      "Alto": 0.88,
      "Crítico": 0.90
    }
  }
}
```

---

## ✅ Checklist de Buenas Prácticas

- [x] Cada entrenamiento genera una carpeta con timestamp
- [x] Se guarda `metadata.json` con hiperparámetros y métricas
- [x] Se guardan visualizaciones (confusion matrix, feature importance)
- [x] La versión actual en `apps/ml/models/` siempre está actualizada
- [x] Cada versión es independiente y reproducible
- [x] Fácil hacer rollback si algo falla

---

## 🔧 Monitoreo Continuo

Para monitorear el desempeño del modelo en el tiempo, puedes hacer un script que:

```python
import json
import os
from pathlib import Path

# Leer todas las versiones
versions_dir = Path('apps/ml/logs/model_versions')
versions = sorted(os.listdir(versions_dir))

print("Histórico de Accuracy:")
for v in versions:
    with open(f'{versions_dir}/{v}/metadata.json') as f:
        meta = json.load(f)
        acc = meta['metrics']['accuracy_test']
        print(f"  {v}: {acc:.2%}")
```

---

## 📚 Referencias

- **MLOps Basics**: https://mlops.community/
- **Model Registry**: https://mlflow.org/
- **Version Control for ML**: https://dvc.org/

---

**Última actualización:** 2026-06-03
**Creado para:** Healthcare ETL Platform
