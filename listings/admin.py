from django.contrib import admin

from .models import Category, Favorite, Listing, ListingImage


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "transaction_type",
        "price",
        "region",
        "status_badge",
        "is_vip",
        "is_urgent",
        "created_at",
    )
    list_filter = ("status", "category", "transaction_type", "region", "is_vip", "is_urgent")
    search_fields = ("title", "description", "district")
    readonly_fields = ("views_count", "created_at", "updated_at", "owner")
    inlines = [ListingImageInline]
    actions = ["approve_listings", "reject_listings"]

    @admin.display(description="Status")
    def status_badge(self, obj):
        return obj.get_status_display()

    @admin.action(description="Seçilmiş elanları təsdiqlə")
    def approve_listings(self, request, queryset):
        queryset.update(status=Listing.Status.APPROVED)

    @admin.action(description="Seçilmiş elanları rədd et")
    def reject_listings(self, request, queryset):
        queryset.update(status=Listing.Status.REJECTED)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "created_at")
