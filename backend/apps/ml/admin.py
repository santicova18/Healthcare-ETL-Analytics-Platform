from django.contrib import admin

from .models import ModelVersion, PredictionLog


@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    list_display = ("version", "algorithm", "accuracy", "is_active", "created_at")
    list_filter = ("is_active", "algorithm")
    search_fields = ("version",)


@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ("patient", "model_version", "prediction", "probability", "created_at")
    list_filter = ("prediction",)
    readonly_fields = ("created_at",)
