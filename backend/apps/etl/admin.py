from django.contrib import admin

from .models import ETLHistory, ETLRun


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


@admin.register(ETLHistory)
class ETLHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "file_name",
        "file_hash_short",
        "records_processed",
        "records_inserted",
        "records_duplicates",
        "processed_at",
    )
    readonly_fields = ("file_hash", "file_name", "records_processed", "records_inserted", "records_duplicates", "processed_at")
    search_fields = ("file_name", "file_hash")

    def file_hash_short(self, obj):
        return obj.file_hash[:16] + "..."

    file_hash_short.short_description = "Hash (SHA256)"
