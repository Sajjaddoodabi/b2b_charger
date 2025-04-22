from rest_framework import serializers

from vendor.models import Vendor


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def to_representation(self, instance):
        from user.serializers import UserInfoSerializer

        response = super().to_representation(instance)

        response["user"] = UserInfoSerializer(
            instance.user, context={"request": self.context["request"]}
        ).data

        return response


class VendorInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        exclude = ["balance"]
        read_only_fields = ["created_at", "updated_at"]

    def to_representation(self, instance):
        from user.serializers import UserInfoSerializer

        response = super().to_representation(instance)

        response["user"] = UserInfoSerializer(
            instance.user, context={"request": self.context["request"]}
        ).data

        return response
