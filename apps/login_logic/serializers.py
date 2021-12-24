from rest_framework import serializers

from apps.login_logic.models import FinalUserModel


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalUserModel
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
            "is_active": {"write_only": True},
            "date_joined": {"write_only": True},
        }
