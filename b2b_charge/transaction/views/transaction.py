import logging
import uuid

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework import status as http_status
from rest_framework.exceptions import (
    NotFound,
    ParseError,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response

from transaction.filters import TransactionFilter
from transaction.models import Transaction
from transaction.serializers import TransactionSerializer
from transaction.utils import process_transaction
from user.permissions import IsVendorOrAdmin, is_admin
from utils.views import BaseModelViewSet
from vendor.models import Vendor
from django.db import transaction as db_transaction

logger = logging.getLogger(__name__)


class TransactionViewSet(BaseModelViewSet):
    permission_classes = [IsVendorOrAdmin]
    serializer_class = TransactionSerializer
    filterset_class = TransactionFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        "vendor__name",
        "creator__username",
        "description",
    ]

    def get_queryset(self):
        queryset = Transaction.objects.select_related("vendor", "creator").order_by(
            "-id"
        )
        for_manage = self.request.GET.get("for_manage", "false") == "true"

        if is_admin(self.request.user) and for_manage:
            return queryset

        return queryset.filter(vendor__user=self.request.user, vendor__is_active=True)

    @swagger_auto_schema(
        operation_description="Create a new transaction (deposit or withdrawal).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "vendor": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the vendor for what the transaction is being made.",
                ),
                "transaction_type": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Type of transaction (e.g., Deposit, Withdrawal).",
                ),
                "amount": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Amount for the transaction.",
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Optional description for the transaction.",
                ),
            },
            required=["vendor", "transaction_type", "amount"],
        ),
        responses={
            200: openapi.Response("Transaction successful."),
            400: "Bad Request (e.g., missing or invalid data).",
            404: "Vendor not found.",
            500: "Unexpected error occurred.",
        },
    )
    def create(self, request):
        """
        Handle deposit or withdrawal transactions for a vendor.
        """
        if not is_admin(request.user):
            logger.warning(
                f"TRANSACTION CREATE: User {request.user.username} attempted to create a transaction without admin privileges."
            )
            raise PermissionDenied("You do not have permission to create transactions.")

        vendor_id = request.data.get("vendor")
        transaction_type = request.data.get("transaction_type")
        amount = request.data.get("amount")
        description = request.data.get("description", "")

        if not all([vendor_id, transaction_type, amount]):
            logger.warning(
                "TRANSACTION CREATE: Missing required fields for transaction creation."
            )
            raise ParseError()

        with db_transaction.atomic():
            try:
                vendor = Vendor.objects.select_for_update().get(id=vendor_id)
                amount = int(amount)
                transfer_id = uuid.uuid4()

                error, proccess_status = process_transaction(
                    transaction_type,
                    vendor,
                    amount,
                    request.user,
                    description,
                    transfer_id,
                )

                if not proccess_status:
                    logger.warning(error["log"])
                    return Response(
                        {"message": error["message"]},
                        status=http_status.HTTP_400_BAD_REQUEST,
                    )

                logger.info(
                    f"TRANSACTION CREATE: Transaction successful. Vendor: {vendor.name}, Type: {transaction_type}, Amount: {amount}, Admin: {request.user.username}"
                )
                return Response(
                    {"message": f"{transaction_type} successful."},
                    status=http_status.HTTP_200_OK,
                )

            except Vendor.DoesNotExist:
                logger.error(f"TRANSACTION CREATE: Vendor with ID {vendor_id} not found.")
                raise NotFound("Vendor not found.")
            except ValueError:
                logger.error(f"TRANSACTION CREATE: Invalid amount value provided: {amount}")
                raise ParseError("Amount must be a valid integer.")
            except Exception as e:
                logger.exception(
                    f"TRANSACTION CREATE: Unexpected error during transaction creation: {str(e)}"
                )
                raise ValidationError("An unexpected error occurred")

    @swagger_auto_schema(
        operation_description="Update a transaction (not allowed).",
        responses={
            403: "Editing transactions is not allowed.",
        },
    )
    def update(self, request, *args, **kwargs):
        """
        Prevent editing transactions.
        """
        if not request.user.is_superuser:
            raise ValidationError("Transactions cannot be edited.")
        super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a transaction (not allowed).",
        responses={
            403: "Deleting transactions is not allowed.",
        },
    )
    def destroy(self, request, *args, **kwargs):
        """
        Prevent deleting transactions.
        """
        if not request.user.is_superuser:
            raise ValidationError("Transactions cannot be deleted.")
        super().destroy(request, *args, **kwargs)
