from rest_framework import serializers

from transaction.models import Transaction
from user.serializers import UserInfoSerializer
from vendor.serializers import VendorInfoSerializer


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["vendor"] = VendorInfoSerializer(
            instance.vendor, context={"request": self.context.get("request")}
        ).data
        response["creator"] = UserInfoSerializer(
            instance.creator, context={"request": self.context.get("request")}
        ).data
        return response
