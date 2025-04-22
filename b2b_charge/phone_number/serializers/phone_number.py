from rest_framework import serializers

from phone_number.models import PhoneNumber
from user.serializers import UserInfoSerializer


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["creator"] = UserInfoSerializer(
            instance.creator, context={"request": self.context.get("request")}
        ).data
        return response
