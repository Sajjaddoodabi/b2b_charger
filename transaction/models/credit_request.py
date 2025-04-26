from django.db import models
from django.db import transaction as db_transaction
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError

from transaction.models import Transaction
from utils.models import BaseModel
from vendor.models import Vendor
from transaction.utils import process_transaction
import uuid


class CreditRequest(BaseModel):
    class Status(models.TextChoices):
        PENDING = "Pending"
        ACCEPTED = "Accepted"
        REJECTED = "Rejected"
        CANCELLED = "Cancelled"

    vendor = models.ForeignKey("vendor.Vendor", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    approved_by = models.ForeignKey(
        "user.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_credits",
    )
    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.PENDING
    )
    description = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.amount} - {self.status}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Amount must be greater than zero.")

        # prevent multiple PENDING requests per vendor
        if self.status == self.Status.PENDING:
            existing_pending = CreditRequest.objects.filter(
                vendor=self.vendor, status=self.Status.PENDING
            ).exclude(pk=self.pk)
            if existing_pending.exists():
                raise ValidationError("Vendor already has a pending credit request.")

        # if status is not pending, approved_by must be set
        if (
            self.status in [self.Status.ACCEPTED, self.Status.REJECTED]
            and not self.approved_by
        ):
            raise ValidationError(
                "Approval or rejection must include an approved_by user."
            )

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def approve(self, approver):
        if self.status != self.Status.PENDING:
            raise ValidationError("Only pending requests can be approved.")

        transfer_id = uuid.uuid4()

        error, procesess_status = process_transaction(
            transaction_type=Transaction.TransactionType.DEPOSIT,
            vendor=self.vendor,
            amount=self.amount,
            creator=approver,
            description=f"Credit request approved by {approver.username} with amount {self.amount}",
            transfer_id=transfer_id,
        )
        if not procesess_status:
            raise ValidationError(f"Transaction failed: {error}")

        with db_transaction.atomic():
            credit = CreditRequest.objects.select_for_update().get(pk=self.pk)

            if credit.status != self.Status.PENDING:
                raise ValidationError("This request has already been processed.")

            credit.status = self.Status.ACCEPTED
            credit.approved_by = approver
            credit.responded_at = now()
            credit.save()
