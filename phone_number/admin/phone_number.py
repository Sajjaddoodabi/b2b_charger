from django.contrib import admin

from phone_number.models import PhoneNumber


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ["number", "label", "credit", "is_active", "last_recharged_at"]
    list_filter = ["is_active"]
    autocomplete_fields = ["creator"]
    readonly_fields = ["created_at", "updated_at", "last_recharged_at"]
    search_fields = ["number", "creator__username", "label"]
