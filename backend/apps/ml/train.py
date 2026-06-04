import pandas as pd
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, precision_recall_fscore_support
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
from apps.patients.models import Patient
import os

def train_risk_model():
    try:
        # 0. GENERAR TIMESTAMP PARA VERSIONADO
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_name = f"v_{timestamp}"
        
        # Crear directorios de versión
        version_dir = f'apps/ml/logs/model_versions/{version_name}'
        os.makedirs(version_dir, exist_ok=True)
        os.makedirs('apps/ml/models', exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"🚀 ENTRENAMIENTO DE MODELO - {version_name}")
        print(f"{'='*70}\n")

        # 1. Obtener datos desde la BD (Solo campos numéricos para el ML)
        queryset = Patient.objects.all().values(
            'edad', 'imc', 'presion_sistolica', 'presion_diastolica', 
            'glucosa', 'colesterol', 'riesgo_enfermedad'
        )
        df = pd.DataFrame(list(queryset))
        
        if df.empty:
            return "No hay datos suficientes para entrenar el modelo."

        # 2. Codificar variables categóricas (riesgo_enfermedad) - ORDEN FIJO
        class_order = ['Bajo', 'Medio', 'Alto', 'Crítico']
        le = LabelEncoder()
        le.fit(class_order)
        y_encoded = le.transform(df['riesgo_enfermedad'].astype(str))
        
        df_numeric = df[['edad', 'imc', 'presion_sistolica', 'presion_diastolica', 'glucosa', 'colesterol']].fillna(0)

        # 3. ESCALAR FEATURES
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_numeric)
        df_scaled = pd.DataFrame(X_scaled, columns=df_numeric.columns)

        # 4. Generar matriz de correlación
        df_corr = df_scaled.copy()
        df_corr['riesgo_enfermedad'] = y_encoded
        plt.figure(figsize=(10, 8))
        sns.heatmap(df_corr.corr(), annot=True, cmap='coolwarm', fmt='.2f')
        plt.title(f"Correlación de Variables Clínicas - {version_name}")
        plt.tight_layout()
        plt.savefig(f'{version_dir}/correlation_matrix.png', dpi=100)
        plt.savefig('apps/ml/models/correlation_matrix.png', dpi=100)  # Copiar a actual
        plt.close()

        # 5. Preparar Features (X) y Target (y)
        X = df_scaled
        y = y_encoded

        # 6. ESTRATIFICADO SPLIT
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # 7. BALANCEAR CLASES CON SMOTE
        smote = SMOTE(random_state=42, k_neighbors=3)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
        
        dist_before = np.bincount(y_train)
        dist_after = np.bincount(y_train_balanced)
        
        print(f"📊 Distribución de clases:")
        print(f"  ANTES de SMOTE: {dict(zip(le.classes_, dist_before))}")
        print(f"  DESPUÉS de SMOTE: {dict(zip(le.classes_, dist_after))}\n")

        # 8. Entrenar modelo
        model = RandomForestClassifier(
            n_estimators=150,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train_balanced, y_train_balanced)

        # 9. Evaluar modelo
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)
        y_pred_train = model.predict(X_train_balanced)
        
        accuracy_train = (y_pred_train == y_train_balanced).mean()
        accuracy_test = (y_pred == y_test).mean()
        
        # Métricas por clase
        precision, recall, f1, support = precision_recall_fscore_support(
            y_test, y_pred, zero_division=0
        )
        
        report = classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0)
        
        print(f"📈 Métricas de Desempeño:")
        print(f"  Accuracy Train: {accuracy_train:.2%}")
        print(f"  Accuracy Test:  {accuracy_test:.2%}\n")

        # 10. Generar Matriz de Confusión
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(10, 8))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=le.classes_)
        disp.plot(cmap=plt.cm.Blues)
        plt.title(f"Matriz de Confusión - {version_name}")
        plt.tight_layout()
        plt.savefig(f'{version_dir}/confusion_matrix.png', dpi=100)
        plt.savefig('apps/ml/models/confusion_matrix.png', dpi=100)  # Copiar a actual
        plt.close()

        # 11. Feature Importance
        feature_importance = pd.DataFrame({
            'feature': df_numeric.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Graficar feature importance
        plt.figure(figsize=(10, 6))
        plt.barh(feature_importance['feature'], feature_importance['importance'])
        plt.xlabel('Importancia')
        plt.title(f'Feature Importance - {version_name}')
        plt.tight_layout()
        plt.savefig(f'{version_dir}/feature_importance.png', dpi=100)
        plt.close()

        # 12. Guardar MODELO (versión actual + histórico)
        print("💾 Guardando artefactos del modelo...")
        
        # Guardar en versión con timestamp
        joblib.dump(model, f'{version_dir}/risk_model.pkl')
        joblib.dump(scaler, f'{version_dir}/scaler.pkl')
        joblib.dump(le, f'{version_dir}/label_encoder.pkl')
        
        # Guardar en models/ (para que predict.py las use)
        joblib.dump(model, 'apps/ml/models/risk_model.pkl')
        joblib.dump(scaler, 'apps/ml/models/scaler.pkl')
        joblib.dump(le, 'apps/ml/models/label_encoder.pkl')

        # 13. Crear archivo de METADATOS (importante para tracking)
        metadata = {
            "version": version_name,
            "timestamp": datetime.now().isoformat(),
            "dataset": {
                "total_samples": len(df),
                "train_samples": len(X_train_balanced),
                "test_samples": len(X_test),
                "features": df_numeric.columns.tolist(),
                "classes": le.classes_.tolist()
            },
            "class_distribution": {
                "before_smote": dict(zip(le.classes_, dist_before.tolist())),
                "after_smote": dict(zip(le.classes_, dist_after.tolist()))
            },
            "hyperparameters": {
                "n_estimators": 150,
                "max_depth": 15,
                "min_samples_split": 5,
                "min_samples_leaf": 2,
                "class_weight": "balanced"
            },
            "metrics": {
                "accuracy_train": float(accuracy_train),
                "accuracy_test": float(accuracy_test),
                "precision_per_class": dict(zip(le.classes_, precision.tolist())),
                "recall_per_class": dict(zip(le.classes_, recall.tolist())),
                "f1_per_class": dict(zip(le.classes_, f1.tolist()))
            },
            "techniques_applied": [
                "StandardScaler",
                "SMOTE",
                "class_weight='balanced'",
                "Stratified Train/Test Split"
            ]
        }
        
        with open(f'{version_dir}/metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # 14. Guardar reportes
        with open(f'{version_dir}/classification_report.txt', 'w', encoding='utf-8') as f:
            f.write("REPORTE DE CLASIFICACION\n")
            f.write("="*60 + "\n\n")
            f.write(report)
        
        feature_importance.to_csv(f'{version_dir}/feature_importance.csv', index=False)
        
        # Crear archivo de resumen
        summary = f"""
╔════════════════════════════════════════════════════════════╗
║     RESUMEN DE ENTRENAMIENTO DEL MODELO                    ║
╚════════════════════════════════════════════════════════════╝

Fecha: {version_name}
Timestamp: {datetime.now().isoformat()}

DATASET
─────────────────────────────────────────────────────────────
  Total de muestras: {len(df)}
  Muestras de entrenamiento: {len(X_train_balanced)}
  Muestras de test: {len(X_test)}
  Features: {', '.join(df_numeric.columns)}

BALANCEO DE CLASES
─────────────────────────────────────────────────────────────
  ANTES de SMOTE: {dict(zip(le.classes_, dist_before.tolist()))}
  DESPUES de SMOTE: {dict(zip(le.classes_, dist_after.tolist()))}

DESEMPEÑO
─────────────────────────────────────────────────────────────
  Accuracy Train: {accuracy_train:.2%}
  Accuracy Test:  {accuracy_test:.2%}

METRICAS POR CLASE
─────────────────────────────────────────────────────────────
{report}

TECNICAS APLICADAS
─────────────────────────────────────────────────────────────
  [OK] StandardScaler (Escalado de features)
  [OK] SMOTE (Balanceo de clases minoritarias)
  [OK] class_weight='balanced' (Penalizacion de errores)
  [OK] Stratified Split (Proporcion consistente)

ARCHIVOS GENERADOS
─────────────────────────────────────────────────────────────
  Modelo: {version_dir}/risk_model.pkl
  Scaler: {version_dir}/scaler.pkl
  Encoder: {version_dir}/label_encoder.pkl
  Matriz de Confusion: {version_dir}/confusion_matrix.png
  Feature Importance: {version_dir}/feature_importance.png
  Metadatos: {version_dir}/metadata.json
  Reporte: {version_dir}/classification_report.txt

ESTADO: ENTRENAMIENTO COMPLETADO
"""
        
        with open(f'{version_dir}/RESUMEN.txt', 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(summary)
        print(f"\n[OK] Modelo guardado en: {version_dir}")
        print(f"[OK] Modelo actual actualizado en: apps/ml/models/\n")
        
        return summary
        
    except Exception as e:
        import traceback
        error_msg = f"❌ Error durante el entrenamiento del modelo: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return error_msg