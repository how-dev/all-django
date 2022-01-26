import random

from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token


class GenericErrors:
    def __init__(self):
        pass
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
                "result": "The param 'file_type' is not supported.",
            },
            "status": status.HTTP_403_FORBIDDEN,
        },
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


class CPFLogics:
    def __init__(self):
        pass
    @staticmethod
    def format_cpf(cpf):
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    @staticmethod
    def get_digit_algorithm(cpf):
        cpf_verify = list(cpf)
        cpf_verify.reverse()

        sum_char = 0
        count = 2
        for char in cpf_verify:
            sum_char += int(char) * count
            count += 1

        cpf_verify.reverse()
        cpf_verify = "".join(cpf_verify)

        rest = sum_char % 11

        if rest < 2:
            return cpf_verify + "0"

        digit = str(11 - rest)

        return cpf_verify + digit

    def random_eleven_digits(self):
        cpf = ""

        for _ in range(11):
            cpf += str(random.randrange(0, 10))

        cpf_verify = cpf[:9]
        for _ in range(2):
            cpf_verify = self.get_digit_algorithm(cpf_verify)

        if cpf == cpf_verify:
            return cpf
        else:
            return False

    def force_valid_cpf(self):
        cpf = self.random_eleven_digits()
        if cpf is not False:
            return cpf
        else:
            return self.force_valid_cpf()

