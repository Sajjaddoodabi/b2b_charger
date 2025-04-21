from rest_framework import serializers

from transaction.models import Transaction
from user.serializers import UserInfoSerializer
from vendor.serializers import VendorInfoSerializer


class TransactionSerializer(serializers.ModelSerializer):
    persian_created_at = serializers.ReadOnlyField()
    persian_updated_at = serializers.ReadOnlyField()

    class Meta:
        model = Transaction
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["vendor"] = VendorInfoSerializer(
            instance.vendor, context={"request": self.context.get("request")}
        ).data
        response["creator"] = UserInfoSerializer(
            instance.user, context={"request": self.context.get("request")}
        ).data
        return response
