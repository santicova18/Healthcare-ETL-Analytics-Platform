from django.contrib import admin

from .models import ETLRun


@admin.register(ETLRun)
class ETLRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "records_processed",
        "elapsed_seconds",
        "started_at",
        "finished_at",
        "user",
    )
    list_filter = ("status",)
    readonly_fields = ("started_at",)
