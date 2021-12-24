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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["password"] = make_password(serializer.validated_data["password"])
        self.perform_create(serializer)

        user = FinalUserModel.objects.get(id=serializer.data["id"])
        token = Token.objects.create(user=user)
        headers = self.get_success_headers(serializer.data)

        data = serializer.data
        data["token"] = token.key

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class BaseLogin(APIView, GenericErrors):
    def post(self, request):
        data = request.data

        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        email = data['email']
        password = data['password']

        try:
            user = FinalUserModel.objects.get(email=email)
        except FinalUserModel.DoesNotExist:
            response = self.failure_result()
            return Response(**response)

        is_valid_password = check_password(password, user.password)

        if is_valid_password:
            user.last_login = timezone.now()
            user.save()
            data = UserSerializer(user).data

            token = Token.objects.get_or_create(user=user)[0]
            reset_token = ResetToken(token.key, user, 1)
            token = reset_token.reset_token()
            data["token"] = token.key

            response = self.success_result(data)
            return Response(**response)
        else:
            response = self.failure_result()
            return Response(**response)

