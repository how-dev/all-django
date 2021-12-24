from django.contrib.auth.models import User
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
