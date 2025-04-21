from rest_framework import serializers

from vendor.models import Vendor


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"

    def to_representation(self, instance):
        from user.serializers import UserInfoSerializer

        response = super().to_representation(instance)

        response["user"] = UserInfoSerializer(
            instance.user, context={"request": self.context["request"]}
        ).data

        return response
