import pandas as pd
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    precision_recall_fscore_support,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
from apps.patients.models import Patient
import os
from pathlib import Path

_ML_DIR = Path(__file__).resolve().parent
_MODELS_DIR = _ML_DIR / "models"
_LOGS_VERSIONS_DIR = _ML_DIR / "logs" / "model_versions"


def train_risk_model():
    try:
        # 0. GENERAR TIMESTAMP PARA VERSIONADO
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_name = f"v_{timestamp}"

        # Crear directorios de versión
        version_dir = _LOGS_VERSIONS_DIR / version_name
        version_dir.mkdir(parents=True, exist_ok=True)
        _MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"[TRAIN] ENTRENAMIENTO DE MODELO - {version_name}")
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
        plt.savefig(version_dir / "correlation_matrix.png", dpi=100)
        plt.savefig(_MODELS_DIR / "correlation_matrix.png", dpi=100)
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
        
        print(f"Distribucion de clases:")
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

        # Métricas globales (weighted) - multiclase
        precision_weighted_test = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall_weighted_test = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1_weighted_test = f1_score(y_test, y_pred, average='weighted', zero_division=0)

        # AUC-ROC multiclase (One-vs-Rest)
        auc_roc_weighted_test = roc_auc_score(
            y_test,
            y_pred_proba,
            multi_class='ovr',
            average='weighted'
        )

        # Métricas por clase
        precision, recall, f1, support = precision_recall_fscore_support(
            y_test, y_pred, zero_division=0
        )

        
        report = classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0)
        
        print(f"Metricas de Desempeno:")
        print(f"  Accuracy Train: {accuracy_train:.2%}")
        print(f"  Accuracy Test:  {accuracy_test:.2%}\n")

        # 10. Generar Matriz de Confusión (y figura combinada con ROC multiclase)
        cm = confusion_matrix(y_test, y_pred)

        # 10.1. Matriz de confusión sola (archivo existente)
        plt.figure(figsize=(10, 8))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=le.classes_)
        disp.plot(cmap=plt.cm.Blues)
        plt.title(f"Matriz de Confusión - {version_name}")
        plt.tight_layout()
        plt.savefig(version_dir / "confusion_matrix.png", dpi=100)
        plt.savefig(_MODELS_DIR / "confusion_matrix.png", dpi=100)
        plt.close()

        # 10.2. Figura combinada: Matriz de confusión + Curva ROC (one-vs-rest)
        # Nota: y_test y y_pred están en espacio codificado (0..n_classes-1)
        # y_pred_proba tiene probabilidades por clase en el mismo orden de clases codificadas.
        from sklearn.preprocessing import label_binarize
        from sklearn.metrics import roc_curve, auc

        Y_test_bin = label_binarize(y_test, classes=np.arange(len(le.classes_)))
        if Y_test_bin.ndim == 1:
            Y_test_bin = np.vstack([1 - Y_test_bin, Y_test_bin]).T

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Matriz de confusión en subgráfica izquierda
        ConfusionMatrixDisplay.from_predictions(
            y_test,
            y_pred,
            display_labels=le.classes_,
            ax=axes[0],
            cmap=plt.cm.Blues,
            colorbar=False,
            values_format="d",
        )
        axes[0].set_title("Matriz de Confusión")

        # Curva ROC en subgráfica derecha
        for class_idx, class_name in enumerate(le.classes_):
            fpr, tpr, _ = roc_curve(Y_test_bin[:, class_idx], y_pred_proba[:, class_idx])
            roc_auc = auc(fpr, tpr)
            axes[1].plot(fpr, tpr, label=f"{class_name} (AUC={roc_auc:.2f})")

        axes[1].plot([0, 1], [0, 1], "k--", label="Aleatorio")
        axes[1].set_xlabel("FPR")
        axes[1].set_ylabel("TPR")
        axes[1].set_title("Curva ROC")
        axes[1].legend(loc="lower right")

        plt.tight_layout()
        plt.savefig(version_dir / "confusion_matrix_roc_combined.png", dpi=150)
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
        plt.savefig(version_dir / "feature_importance.png", dpi=100)
        plt.close()

        # 12. Guardar MODELO (versión actual + histórico)
        print("Guardando artefactos del modelo...")
        
        # Guardar en versión con timestamp
        joblib.dump(model, version_dir / "risk_model.pkl")
        joblib.dump(scaler, version_dir / "scaler.pkl")
        joblib.dump(le, version_dir / "label_encoder.pkl")

        joblib.dump(model, _MODELS_DIR / "risk_model.pkl")
        joblib.dump(scaler, _MODELS_DIR / "scaler.pkl")
        joblib.dump(le, _MODELS_DIR / "label_encoder.pkl")

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
                "precision_weighted_test": float(precision_weighted_test),
                "recall_weighted_test": float(recall_weighted_test),
                "f1_weighted_test": float(f1_weighted_test),
                "auc_roc_weighted_test": float(auc_roc_weighted_test),
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
        
        with open(version_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        with open(version_dir / "classification_report.txt", "w", encoding="utf-8") as f:
            f.write("REPORTE DE CLASIFICACION\n")
            f.write("="*60 + "\n\n")
            f.write(report)
        
        feature_importance.to_csv(version_dir / "feature_importance.csv", index=False)
        
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
        
        with open(version_dir / "RESUMEN.txt", "w", encoding="utf-8") as f:
            f.write(summary)

        print(summary)
        print(f"\n[OK] Modelo guardado en: {version_dir}")
        print(f"[OK] Modelo actual actualizado en: {_MODELS_DIR}\n")
        
        # Persistencia de auditoría en base de datos (solo extender, no reemplazar artefactos)
        try:
            from apps.ml.models import ModelVersion

            ModelVersion.objects.filter(is_active=True).update(is_active=False)

            metadata_features = metadata.get("dataset", {}).get("features", [])
            metrics = metadata.get("metrics", {})
            dataset_total = int(metadata.get("dataset", {}).get("total_samples", len(df)))

            # Derivamos accuracy/precision/recall/f1 de los campos existentes en metadata.
            # accuracy_test no está seteado directamente como accuracy, pero sí está en metrics.
            accuracy_val = None
            if "accuracy_test" in metadata.get("metrics", {}):
                accuracy_val = metadata["metrics"]["accuracy_test"]
            elif "accuracy_train" in metadata.get("metrics", {}):
                accuracy_val = metadata["metrics"]["accuracy_train"]

            ModelVersion.objects.update_or_create(
                version=version_name,
                defaults={
                    "algorithm": "RandomForestClassifier",
                    "dataset_size": dataset_total,
                    "feature_schema": metadata_features,
                    "accuracy": accuracy_val,
                    "precision": metrics.get("precision_per_class", {}),
                    "recall": metrics.get("recall_per_class", {}),
                    "f1_score": metrics.get("f1_per_class", {}),
                    "model_path": str(version_dir / "risk_model.pkl"),
                    "metadata_path": str(version_dir / "metadata.json"),
                    "is_active": True,
                },
            )
            print(f"[OK] ModelVersion registrado en BD: {version_name}")
        except Exception as db_e:
            import traceback
            print(f"[WARN] Persistencia ModelVersion falló: {db_e}")
            print(f"[WARN] Traceback: {traceback.format_exc()}")

        return summary
        
    except Exception as e:
        import traceback
        error_msg = f"Error durante el entrenamiento del modelo: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return error_msg