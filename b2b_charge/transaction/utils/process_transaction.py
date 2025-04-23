from django.db import transaction as db_transaction
from django.db.utils import OperationalError
import time
from transaction.models import Transaction
from vendor.models import Vendor


def process_transaction(
    transaction_type,
    vendor,
    amount,
    creator=None,
    description="",
    phone_number=None,
    transfer_id=None,
    retries=3,
    retry_wait=0.2,
):
    """
    Process a transaction with automatic retry if lock timeout occurs.
    """
    error = {"log": "", "message": ""}

    if amount <= 0:
        error["log"] = f"❌ Invalid amount: {amount}"
        error["message"] = "Amount must be greater than zero."
        return error, False

    for attempt in range(retries):
        try:
            with db_transaction.atomic():
                locked_vendor = Vendor.objects.select_for_update(skip_locked=True).get(
                    pk=vendor.pk
                )

                if transaction_type == Transaction.TransactionType.DEPOSIT:
                    locked_vendor.balance += amount

                elif transaction_type == Transaction.TransactionType.WITHDRAW:
                    if locked_vendor.balance < amount:
                        error["log"] = (
                            f"❌ Insufficient balance on vendor {locked_vendor.name}"
                        )
                        error["message"] = "Insufficient balance."
                        return error, False
                    locked_vendor.balance -= amount

                else:
                    error["log"] = f"❌ Invalid transaction type: {transaction_type}"
                    error["message"] = "Invalid transaction type."
                    return error, False

                locked_vendor.save(update_fields=["balance"])

                Transaction.objects.create(
                    vendor=locked_vendor,
                    creator=creator,
                    transaction_type=transaction_type,
                    amount=amount,
                    description=description,
                    phone_number=phone_number,
                    transfer_id=transfer_id,
                )
            return error, True

        except OperationalError as e:
            if "Lock wait timeout" in str(e) and attempt < retries - 1:
                continue
            else:
                raise
