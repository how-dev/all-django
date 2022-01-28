import json

from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from services.blr_lib import BRL
from services.import_export import DBToFile
from services.user_flow import GenericErrors, ResetToken, CPFLogics
from .filters import FinalUserFilter
from .models import FinalUserModel
from .permissions import FinalUserPermissions
from .resources import UserResource
from .serializers import LoginSerializer, UserSerializer
from django_filters import rest_framework as filters


class UserViewSet(ModelViewSet, DBToFile, GenericErrors, CPFLogics):
    queryset = FinalUserModel.objects.order_by("id").filter(is_active=True)
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [FinalUserPermissions]
    throttle_classes = [UserRateThrottle]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FinalUserFilter
    scheduler_time = {"minutes": 60}
    supported_files_types = ("xlsx", "csv")

    @method_decorator(cache_page(60, key_prefix="list"))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        cache.set("list", json.dumps(serializer.data))
        return self.get_paginated_response(serializer.data)

    def export_file(self, _, file_type="xlsx"):
        is_supported = self.is_supported(file_type)

        if not is_supported:
            response = self.not_supported_result()
            return Response(**response)

        if file_type == "xlsx":
            excel_response = self.http_excel(UserResource, "users")

            return excel_response

        csv_response = self.http_csv(
            fields=(
                "id",
                "last_login",
                "is_active",
                "date_joined",
                "email",
                "name",
                "document",
            ),
            queryset=self.queryset,
            serializer=self.serializer_class,
            file_name="users",
        )

        return csv_response

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

    def scheduler(self):
        cpf = self.force_valid_cpf()

        queryset = FinalUserModel.objects.order_by("id").filter(document__isnull=True)

        if len(queryset) > 0:
            try:
                FinalUserModel.objects.get(document=cpf)
            except FinalUserModel.DoesNotExist:
                user = queryset[0]
                user.document = cpf
                user.save()
                print(
                    f"I found a valid document. Is a brazilian document, his number is {cpf} and "
                    f"I put this value in the user's document field with id {user.id}"
                )
        else:
            return None


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
