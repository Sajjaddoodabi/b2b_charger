import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status as http_status
from transaction.models import CreditRequest
from transaction.filters import CreditRequestFilter
from transaction.serializers import CreditRequestSerializer
from user.permissions import IsVendorOrAdmin, is_admin
from utils.views import BaseModelViewSet
from vendor.models import Vendor

logger = logging.getLogger(__name__)


class CreditRequestViewSet(BaseModelViewSet):
    permission_classes = [IsVendorOrAdmin]
    serializer_class = CreditRequestSerializer
    filterset_class = CreditRequestFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        "vendor__name",
        "creator__username",
        "description",
    ]

    def get_queryset(self):
        queryset = CreditRequest.objects.select_related("vendor", "approved_by").order_by(
            "-id"
        )
        for_manage = self.request.GET.get("for_manage", "false") == "true"

        if is_admin(self.request.user) and for_manage:
            return queryset

        return queryset.filter(vendor__user=self.request.user, vendor__is_active=True)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status != CreditRequest.Status.PENDING:
            raise ValidationError("Only pending credit requests can be edited.")

        if not is_admin(request.user) and instance.vendor.user != request.user:
            raise ValidationError("You can only edit your own credit requests.")

        allowed_fields = [
            "amount",
            "description",
        ]
        for field in request.data.keys():
            if field not in allowed_fields:
                raise ValidationError(f"Field '{field}' is not editable.")

        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Change credit request status",
        operation_description="""
            Allows vendors to cancel their own credit requests and admins to accept or reject them.
            
            - Vendors can cancel only their own **PENDING** requests.
            - Admins can accept or reject **PENDING** requests only.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["status"],
            properties={
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="New status (Accepted, Rejected, or Cancelled)",
                    enum=[
                        CreditRequest.Status.ACCEPTED,
                        CreditRequest.Status.REJECTED,
                        CreditRequest.Status.CANCELLED,
                    ],
                )
            },
        ),
        responses={
            200: openapi.Response("Status changed successfully"),
            400: openapi.Response("Invalid status or business logic error"),
            403: openapi.Response("Unauthorized status change attempt"),
        },
    )
    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        instance = self.get_object()
        new_status = request.data.get("status")

        if not new_status:
            return Response(
                {"error": "Status field is required."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        if new_status not in [
            CreditRequest.Status.ACCEPTED,
            CreditRequest.Status.REJECTED,
            CreditRequest.Status.CANCELLED,
        ]:
            return Response(
                {
                    "error": "Invalid status. Must be 'Accepted', 'Rejected', or 'Cancelled'."
                },
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        if new_status in [
            CreditRequest.Status.ACCEPTED,
            CreditRequest.Status.REJECTED,
        ] and not is_admin(request.user):
            return Response(
                {"error": "Only admins can accept or reject credit requests."},
                status=http_status.HTTP_403_FORBIDDEN,
            )

        try:
            if new_status == CreditRequest.Status.ACCEPTED:
                instance.approve(request.user)
                return Response({"status": "approved"}, status=http_status.HTTP_200_OK)

            elif new_status == CreditRequest.Status.REJECTED:
                if instance.status != CreditRequest.Status.PENDING:
                    raise ValidationError("Only pending requests can be rejected.")

                instance.status = CreditRequest.Status.REJECTED
                instance.approved_by = request.user
                instance.responded_at = now()
                instance.save()
                return Response({"status": "rejected"}, status=http_status.HTTP_200_OK)

            elif new_status == CreditRequest.Status.CANCELLED:
                if instance.status != CreditRequest.Status.PENDING:
                    raise ValidationError("Only pending requests can be cancelled.")

                instance.status = CreditRequest.Status.CANCELLED
                instance.responded_at = now()
                instance.save()
                return Response({"status": "cancelled"}, status=http_status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": str(e)}, status=http_status.HTTP_400_BAD_REQUEST)
