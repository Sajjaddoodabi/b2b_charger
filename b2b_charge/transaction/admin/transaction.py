from django.contrib import admin

from transaction.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["vendor", "transaction_type", "amount", "description"]
    list_filter = ["transaction_type"]
    autocomplete_fields = ["vendor"]
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ["vendor__name", "description"]
