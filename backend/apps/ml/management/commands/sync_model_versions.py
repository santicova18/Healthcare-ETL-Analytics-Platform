import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.ml.models import ModelVersion


_LOGS_VERSIONS_DIR = Path(__file__).resolve().parent.parent.parent / "logs" / "model_versions"


class Command(BaseCommand):
    help = "Sincroniza versiones de modelos desde disco a la base de datos"

    def handle(self, *args, **options):
        if not _LOGS_VERSIONS_DIR.exists():
            self.stdout.write(self.style.ERROR(f"Directorio no encontrado: {_LOGS_VERSIONS_DIR}"))
            return

        version_dirs = sorted([
            d for d in _LOGS_VERSIONS_DIR.iterdir()
            if d.is_dir() and d.name.startswith("v_")
        ])

        if not version_dirs:
            self.stdout.write(self.style.WARNING("No se encontraron versiones de modelo en disco."))
            return

        created = 0
        skipped = 0

        for version_dir in version_dirs:
            version_name = version_dir.name
            metadata_path = version_dir / "metadata.json"
            model_path = version_dir / "risk_model.pkl"

            if ModelVersion.objects.filter(version=version_name).exists():
                self.stdout.write(f"  [SKIP] {version_name} — ya existe en BD")
                skipped += 1
                continue

            metadata = {}
            if metadata_path.exists():
                try:
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(
                        f"  [WARN] Error leyendo {metadata_path}: {e}"
                    ))

            metrics = metadata.get("metrics", {})
            dataset_info = metadata.get("dataset", {})

            accuracy_val = metrics.get("accuracy_test") or metrics.get("accuracy_train")

            ModelVersion.objects.update_or_create(
                version=version_name,
                defaults={
                    "algorithm": "RandomForestClassifier",
                    "dataset_size": dataset_info.get("total_samples", 0),
                    "feature_schema": dataset_info.get("features", []),
                    "accuracy": accuracy_val,
                    "precision": metrics.get("precision_per_class", {}),
                    "recall": metrics.get("recall_per_class", {}),
                    "f1_score": metrics.get("f1_per_class", {}),
                    "model_path": str(model_path) if model_path.exists() else "",
                    "metadata_path": str(metadata_path) if metadata_path.exists() else "",
                    "is_active": False,
                },
            )
            created += 1
            self.stdout.write(self.style.SUCCESS(f"  [OK] {version_name} — sincronizado"))

        total = created + skipped
        self.stdout.write(self.style.SUCCESS(
            f"\nSincronización completada: {created} creadas, {skipped} omitidas de {total} totales"
        ))

        if created > 0:
            newest = ModelVersion.objects.order_by("-created_at").first()
            if newest:
                ModelVersion.objects.filter(is_active=True).update(is_active=False)
                newest.is_active = True
                newest.save(update_fields=["is_active"])
                self.stdout.write(self.style.SUCCESS(
                    f"Modelo activo actualizado a: {newest.version}"
                ))
