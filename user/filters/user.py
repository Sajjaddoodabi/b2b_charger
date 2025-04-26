import django_filters

from user.models import User


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = [
            "username",
            "user_permissions__name",
            "user_permissions__codename",
            "full_name",
            "phone_number",
        ]
