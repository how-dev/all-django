from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token


class GenericErrors:
    messages = {
        "failure": {
            "data": {
                "status": status.HTTP_401_UNAUTHORIZED,
                "result": "Some field is incorrect",
            },
            "status": status.HTTP_401_UNAUTHORIZED,
        },
        "success": {
            "data": {"status": status.HTTP_200_OK, "result": None},
            "status": status.HTTP_200_OK,
        },
        "not_supported": {
            "data": {
                "status": status.HTTP_403_FORBIDDEN,
                "result": "The param 'file_type' is not supported."
            },
            "status": status.HTTP_403_FORBIDDEN
        }
    }

    def failure_result(self):
        return self.messages["failure"]

    def success_result(self, result):
        message = self.messages["success"]
        message["data"]["result"] = result

        return message

    def not_supported_result(self):
        return self.messages["not_supported"]


class ResetToken:
    def __init__(self, token_key, user, hour=1):
        self.token_key = token_key
        self.user = user
        self.hour = hour

    def verify_token_age(self):
        try:
            token = Token.objects.get(key=self.token_key)
        except Token.DoesNotExist:
            token = Token.objects.create(user=self.user)

        age = abs(token.created - timezone.now()).seconds

        return age

    def reset_token(self):
        token_age = self.verify_token_age()
        is_older = (token_age / (3600 * self.hour)) >= 1

        token = Token.objects.get(key=self.token_key)

        if is_older:
            token.delete()
            token = Token.objects.create(user=self.user)

        return token
