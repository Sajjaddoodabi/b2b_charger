import django_filters

from vendor.models import Vendor


class VendorFilter(django_filters.FilterSet):
    class Meta:
        model = Vendor
        fields = "__all__"
