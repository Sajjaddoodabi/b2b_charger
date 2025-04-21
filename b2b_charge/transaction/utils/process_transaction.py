from django.db import transaction as db_transaction
from transaction.models import Transaction


def process_transaction(
    transaction_type,
    vendor,
    amount,
    creator=None,
    description="",
):
    """
    Process a transaction for a vendor. Handles deposits, withdrawals, and notifications.

    Args:
        transaction_type (str): Type of transaction (e.g., Transaction.DEPOSIT or Transaction.WITHDRAW).
        vendor (Vendor): The vendor associated with the transaction.
        amount (float): The amount for the transaction.
        creator (User, optional): The creator of the transaction (admin or system).
        description (str, optional): A description of the transaction.

    Returns:
        tuple: A dictionary with error details (if any) and a boolean indicating transaction success.
    """

    error = {"log": "", "message": ""}
    transaction_status = False

    if amount <= 0:
        error["log"] = f"TRANSACTION ERROR: Invalid amount ({amount}) for transaction."
        error["message"] = "Amount must be greater than zero."
        return error, transaction_status

    with db_transaction.atomic():
        # Handle deposit transactions
        if transaction_type == Transaction.TransactionType.DEPOSIT:
            vendor.balance += amount
            transaction_status = True

        # Handle withdrawal transactions
        elif transaction_type == Transaction.TransactionType.WITHDRAW:
            if vendor.balance < amount:
                error["log"] = (
                    f"TRANSACTION ERROR: Insufficient points for withdrawal. "
                    f"Vencor: {vendor.name}, Balance: {vendor.balance}, Attempted: {amount}"
                )
                error["message"] = "Insufficient points."
                return error, transaction_status

            vendor.balance -= amount
            transaction_status = True

        # Handle invalid transaction types
        else:
            error["log"] = (
                f"TRANSACTION ERROR: Invalid transaction type: {transaction_type}"
            )
            error["message"] = "Invalid transaction type."
            return error, transaction_status

        # Save updated balance for the vendor
        vendor.save(update_fields=["balance"])

        # Record the transaction
        Transaction.objects.create(
            vendor=vendor,
            creator=creator,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
        )

    return error, transaction_status
