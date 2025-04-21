from django.contrib import admin

from vendor.models import Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ["name", "balance", "is_active"]
    list_filter = ["is_active"]
    autocomplete_fields = ["user"]
    search_fields = ["name"]
