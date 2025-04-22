from rest_framework import serializers

from transaction.models import CreditRequest
from user.serializers import UserInfoSerializer
from vendor.serializers import VendorInfoSerializer


class CreditRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditRequest
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "responded_at"]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["vendor"] = VendorInfoSerializer(
            instance.vendor, context={"request": self.context.get("request")}
        ).data
        response["approved_by"] = UserInfoSerializer(
            instance.approved_by, context={"request": self.context.get("request")}
        ).data
        return response

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        # Use self.instance.vendor if vendor is not passed (PATCH)
        vendor = attrs.get("vendor") or (self.instance.vendor if self.instance else None)

        if not vendor:
            raise serializers.ValidationError({"vendor": "Vendor is required."})

        # Validate ownership
        if vendor.user != user:
            raise serializers.ValidationError({"vendor": "Vendor does not belong to the current user."})

        # Validate active
        if not vendor.is_active:
            raise serializers.ValidationError({"vendor": "Vendor is not active."})

        # Validate amount (only if passed)
        amount = attrs.get("amount") or (self.instance.amount if self.instance else None)
        if amount is None:
            raise serializers.ValidationError({"amount": "Amount is required."})
        if amount <= 0:
            raise serializers.ValidationError({"amount": "Amount must be greater than zero."})

        return attrs

    def validate_vendor(self, value):
        if self.instance and value != self.instance.vendor:
            raise serializers.ValidationError("Vendor cannot be changed after creation.")
        return value