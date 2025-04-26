import django_filters

from phone_number.models import PhoneNumber


class PhoneNumberFilter(django_filters.FilterSet):
    class Meta:
        model = PhoneNumber
        fields = "__all__"
