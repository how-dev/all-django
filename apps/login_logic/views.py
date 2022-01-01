import json
import random

from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from services.import_export import DBToFile
from services.user_flow import GenericErrors, ResetToken
from .models import FinalUserModel
from .resources import UserResource
from .serializers import LoginSerializer, UserSerializer


class UserViewSet(ModelViewSet, DBToFile, GenericErrors):
    queryset = FinalUserModel.objects.all()
    serializer_class = UserSerializer
    scheduler_time = {"minutes": 0.03125}
    supported_files_types = ("xlsx", "csv")

    @method_decorator(cache_page(60, key_prefix="user_cache"))
    def list(self, request, *args, **kwargs):
        # cached = cache.get('estudos')
        #
        # if cached is None:

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        cache.set('estudos', json.dumps(serializer.data))

        return Response(serializer.data)
        # return Response(json.loads(cached))

    def export_file(self, _, file_type="xlsx"):
        is_supported = self.is_supported(file_type)

        if not is_supported:
            response = self.not_supported_result()
            return Response(**response)

        if file_type == "xlsx":
            excel_response = self.http_excel(UserResource, "users")

            return excel_response

        if file_type == "csv":
            csv_response = self.http_csv(
                fields=("id", "last_login", "is_active", "date_joined", "email", "name"),
                queryset=self.queryset,
                serializer=self.serializer_class,
                file_name="users"
            )

            return csv_response

        response = self.failure_result()
        return Response(**response)

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
