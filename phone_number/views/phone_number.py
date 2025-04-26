import logging

from django.db import transaction as db_transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from phone_number.filters import PhoneNumberFilter
from phone_number.models import PhoneNumber
from phone_number.serializers import PhoneNumberSerializer
from transaction.models import Transaction
from transaction.utils import process_transaction
from user.permissions import IsVendorOrAdmin, is_admin
from utils.views import BaseModelViewSet
from vendor.models import Vendor
import uuid

logger = logging.getLogger(__name__)


class PhoneNumberViewSet(BaseModelViewSet):
    permission_classes = [IsVendorOrAdmin]
    serializer_class = PhoneNumberSerializer
    filterset_class = PhoneNumberFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        "vendor__name",
        "creator__username",
        "description",
    ]

    def get_queryset(self):
        queryset = PhoneNumber.objects.select_related("creator").order_by("-id")
        for_manage = self.request.GET.get("for_manage", "false") == "true"

        if is_admin(self.request.user) and for_manage:
            return queryset

        return queryset.filter(is_active=True)

    @swagger_auto_schema(
        operation_summary="Charge a phone number",
        operation_description="Vendors can safely charge a phone number with a given amount.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["amount"],
            properties={
                "amount": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Amount to add to the phone number's credit",
                )
            },
        ),
        responses={
            200: openapi.Response(description="Phone charged successfully."),
            400: "Invalid amount or insufficient vendor balance.",
            403: "Unauthorized",
        },
    )
    @action(detail=True, methods=["post"])
    def charge(self, request, pk=None):
        try:
            amount = float(request.data.get("amount"))
        except (TypeError, ValueError):
            raise ValidationError("Invalid amount.")

        if amount <= 0:
            raise ValidationError("Charge amount must be greater than zero.")

        user = request.user
        transfer_id = uuid.uuid4()

        with db_transaction.atomic():
            try:
                phone = PhoneNumber.objects.select_for_update().get(pk=pk)
                vendor = Vendor.objects.select_for_update().get(
                    user=user, is_active=True
                )

                # Withdraw from vendor (safe via helper)
                error, success = process_transaction(
                    transaction_type=Transaction.TransactionType.WITHDRAW,
                    vendor=vendor,
                    amount=amount,
                    creator=user,
                    phone_number=phone,
                    description=f"Phone charge initiated for {phone.number}",
                    transfer_id=transfer_id,
                )

                if not success:
                    raise ValidationError(error["message"])

                # Apply credit to phone
                phone.credit += amount
                phone.save(update_fields=["credit"])

                # Log deposit to phone
                Transaction.objects.create(
                    transaction_type=Transaction.TransactionType.CHARGE,
                    vendor=vendor,
                    amount=amount,
                    creator=user,
                    phone_number=phone,
                    description=f"Credit applied to phone {phone.number} by {user.username}",
                    transfer_id=transfer_id,
                )

            except PhoneNumber.DoesNotExist:
                raise ValidationError("Phone number not found.")
            except Vendor.DoesNotExist:
                raise ValidationError("Vendor not found.")
            except Exception as e:
                logger.error(f"Error charging phone number: {e}")
                raise ValidationError("An error occurred while processing the charge.")

        return Response(
            {
                "status": "charged",
                "phone_number": phone.number,
                "new_credit": str(phone.credit),
                "vendor_balance": str(vendor.balance),
            },
            status=status.HTTP_200_OK,
        )
