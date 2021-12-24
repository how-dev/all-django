from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

from services.user_flow import GenericErrors
from .serializers import LoginSerializer, UserSerializer


class BaseLogin(APIView, GenericErrors):
    def post(self, request):
        data = request.data

        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        email = data['email']
        password = data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            response = self.failure_result()
            return Response(**response)

        is_valid_password = check_password(password, user.password)

        if is_valid_password:
            data = UserSerializer(user).data
            response = self.success_result(data)
            return Response(**response)
        else:
            return self.failure_result()

