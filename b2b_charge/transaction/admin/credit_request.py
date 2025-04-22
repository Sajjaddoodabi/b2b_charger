from django.contrib import admin

from transaction.models import CreditRequest


@admin.register(CreditRequest)
class CreditRequestAdmin(admin.ModelAdmin):
    list_display = ["vendor", "amount", "approved_by", "status", "description"]
    list_filter = ["status"]
    autocomplete_fields = ["vendor", "approved_by"]
    readonly_fields = ["created_at", "updated_at", "responded_at"]
    search_fields = ["vendor__name", "approved_by__username", "description"]
