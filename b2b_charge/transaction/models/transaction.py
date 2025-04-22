from django.db import models

from utils.models import BaseModel


class Transaction(BaseModel):
    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"
        WITHDRAW = "withdraw", "Withdraw"
        CHARGE = "charge", "Charge"

    vendor = models.ForeignKey(
        "vendor.Vendor", on_delete=models.CASCADE, related_name="transactions"
    )
    phone_number = models.ForeignKey(
        "phone_number.PhoneNumber",
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
    )
    creator = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="admin_transactions",
        null=True,
        blank=True,
    )
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    transfer_id = models.UUIDField(null=True, blank=True, db_index=True)

    def __str__(self):
        return f"{self.transaction_type} {self.amount} - {self.vendor.name}"
