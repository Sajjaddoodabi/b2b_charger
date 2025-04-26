import django_filters

from transaction.models import CreditRequest


class CreditRequestFilter(django_filters.FilterSet):
    class Meta:
        model = CreditRequest
        fields = "__all__"
