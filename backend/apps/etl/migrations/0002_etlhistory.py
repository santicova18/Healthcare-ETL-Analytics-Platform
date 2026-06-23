from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("etl", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ETLHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file_hash", models.CharField(max_length=64, unique=True, verbose_name="Hash SHA256 del archivo")),
                ("file_name", models.CharField(max_length=255, verbose_name="Nombre del archivo")),
                ("records_processed", models.PositiveIntegerField(default=0, verbose_name="Registros procesados (limpios)")),
                ("records_inserted", models.PositiveIntegerField(default=0, verbose_name="Registros insertados (nuevos)")),
                ("records_duplicates", models.PositiveIntegerField(default=0, verbose_name="Registros duplicados ignorados")),
                ("processed_at", models.DateTimeField(auto_now_add=True, verbose_name="Procesado el")),
            ],
            options={
                "verbose_name": "Historial ETL",
                "verbose_name_plural": "Historiales ETL",
                "db_table": "etl_history",
                "ordering": ["-processed_at"],
            },
        ),
    ]
