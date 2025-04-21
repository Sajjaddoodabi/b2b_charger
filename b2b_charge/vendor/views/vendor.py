from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters

from vendor.filters import VendorFilter
from vendor.models import Vendor
from user.permissions import IsVendorOrAdmin, is_admin
from vendor.serializers import VendorSerializer
from utils.views import BaseModelViewSet


class VendorViewSet(BaseModelViewSet):
    permission_classes = [IsVendorOrAdmin]
    serializer_class = VendorSerializer
    filterset_class = VendorFilter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name"]

    def get_queryset(self):
        queryset = Vendor.objects.all().order_by("-id")
        if is_admin(self.request.user):
            return queryset

        return queryset.filter(user=self.request.user, is_active=True)

    @swagger_auto_schema(
        operation_description="Create a new Comapny entry.",
        request_body=VendorSerializer,
        responses={
            201: VendorSerializer,
            400: "Invalid data provided.",
        },
    )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
