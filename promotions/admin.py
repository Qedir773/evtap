from django.contrib import admin

from .models import Promotion


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        "listing",
        "user",
        "plan",
        "amount",
        "currency",
        "status",
        "mock_reference_code",
        "created_at",
        "paid_at",
    )
    list_filter = ("status", "plan")
    readonly_fields = (
        "listing",
        "user",
        "plan",
        "amount",
        "currency",
        "mock_reference_code",
        "created_at",
        "paid_at",
    )
