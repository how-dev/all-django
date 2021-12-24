import random

from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from services.user_flow import GenericErrors, ResetToken
from .models import FinalUserModel
from .serializers import LoginSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    queryset = FinalUserModel.objects.all()
    serializer_class = UserSerializer
    scheduler_time = {"minutes": 0.03125}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["password"] = make_password(
            serializer.validated_data["password"]
        )
        self.perform_create(serializer)

        user = FinalUserModel.objects.get(id=serializer.data["id"])
        token = Token.objects.create(user=user)
        headers = self.get_success_headers(serializer.data)

        data = serializer.data
        data["token"] = token.key

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

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

    def scheduler(self):
        cpf = ""

        for _ in range(11):
            cpf += str(random.randrange(0, 10))

        cpf_verify = cpf[:9]
        for _ in range(2):
            cpf_verify = self.get_digit_algorithm(cpf_verify)

        if cpf == cpf_verify:
            print(
                f"I found! I found! I found a brasilian document wich is valid! "
                f"The document is a CPF and his number is: {cpf}"
            )


class BaseLogin(APIView, GenericErrors):
    def post(self, request):
        data = request.data

        """
            Checks fields in request body with base in "LoginSerializer",
            which requires the email field and password field.
        """
        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        email = data["email"]
        password = data["password"]

        """
            Try get an user by email. If does not exist an user with this email,
            return a generic message of failure.
        """
        try:
            user = FinalUserModel.objects.get(email=email)
        except FinalUserModel.DoesNotExist:
            response = self.failure_result()
            return Response(**response)

        """
            The code here only be executed if obtain success in get an user
            by email. So now we will check the password. Here, we use the 
            "check_password" function to decript the password in database and
            compare with the password wich we recive in request body.
            
            The "check_password" function return True if the password is equals,
            and False to contrary
        """
        is_valid_password = check_password(password, user.password)

        if is_valid_password:
            """
            Here, we will set the "last_login" field with actual hour
            with base in timezone.
            """
            user.last_login = timezone.now()
            user.save()
            data = UserSerializer(user).data

            """
                And now we get or create a Token in database and apply the token reset
                logic. This logic is explained in his class.
            """
            token = Token.objects.get_or_create(user=user)[0]
            reset_token = ResetToken(token.key, user, 1)
            token = reset_token.reset_token()
            data["token"] = token.key

            response = self.success_result(data)
            return Response(**response)
        else:
            """
            If the password is not valid, we return too a generic message of failure,
            because we can't specify if the user missed the email field or the password field.
            """
            response = self.failure_result()
            return Response(**response)
