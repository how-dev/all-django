from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from faker import Faker

from apps.login_logic.models import FinalUserModel

fake = Faker()


class FinalUserEndpointTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.endpoints = {
            "user": "/api/v1/user/",
            "login": "/api/v1/login/",
            "export": lambda file_type: f"/api/v1/export/{file_type}"
        }

        cls.base_user = FinalUserModel.objects.create(
            name=fake.name(),
            email=fake.unique.email(),
            password=make_password(fake.name()),
            is_active=True,
            date_joined=timezone.now(),
            last_login=timezone.now(),
            document="00000000000"
        )

    def test_cant_export_xlsx_unauthenticated(self):
        response = self.client.get(self.endpoints["export"]("xlsx"))

        self.assertEquals(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_cant_export_xlsx_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token foobarbaz")
        response = self.client.get(self.endpoints["export"]("xlsx"))

        self.assertEquals(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_cant_export_xlsx_with_valid_token_invalid_argument(self):
        token = Token.objects.get_or_create(user=self.base_user)[0]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.endpoints["export"]("xlsxx"))

        self.assertEquals(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_cant_export_csv_unauthenticated(self):
        response = self.client.get(self.endpoints["export"]("csv"))

        self.assertEquals(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_cant_export_csv_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token foobarbaz")
        response = self.client.get(self.endpoints["export"]("csv"))

        self.assertEquals(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_cant_list_user_unauthenticated(self):
        response = self.client.get(self.endpoints["user"])

        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cant_list_user_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token foobarbaz")
        response = self.client.get(self.endpoints["user"])

        self.assertEquals(response.data["detail"], "Invalid token.")

    def test_cant_update_user_unauthenticated(self):
        response = self.client.patch(f'{self.endpoints["user"]}1/')

        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cant_update_user_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token foobarbaz")
        response = self.client.patch(f'{self.endpoints["user"]}1/')

        self.assertEquals(response.data["detail"], "Invalid token.")

    def test_cant_delete_user_unauthenticated(self):
        response = self.client.delete(f'{self.endpoints["user"]}1/')

        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cant_delete_user_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token foobarbaz")
        response = self.client.delete(f'{self.endpoints["user"]}1/')

        self.assertEquals(response.data["detail"], "Invalid token.")

    def test_cant_sign_up_with_invalid_body(self):
        body = {
            "email": fake.email(),
            "password": fake.name()
        }

        response = self.client.post(self.endpoints["user"], body)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_sign_up(self):
        body = {
            "name": "test",
            "email": "test@mail.com",
            "password": "test"
        }

        response = self.client.post(self.endpoints["user"], body)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_can_login(self):
        self.test_can_sign_up()
        body = {
            "email": "test@mail.com",
            "password": "test"
        }

        response = self.client.post(self.endpoints["login"], body)

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        try:
            return response.data["result"]["token"]
        except KeyError:
            return False

    def test_can_list_users_authenticated(self):
        token = Token.objects.get_or_create(user=self.base_user)[0]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.get(self.endpoints["user"])

        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_can_patch_users_authenticated(self):
        token = Token.objects.get_or_create(user=self.base_user)[0]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        body = {
            "name": "Foo"
        }

        response = self.client.patch(f'{self.endpoints["user"]}{token.user_id}/', body)

        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_can_delete_users_authenticated(self):
        token = Token.objects.get_or_create(user=self.base_user)[0]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.delete(f'{self.endpoints["user"]}{token.user_id}/')

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_can_export_csv_file(self):
        token = Token.objects.get_or_create(user=self.base_user)[0]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.endpoints["export"]("csv"))

        self.assertEquals(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_can_export_xlsx_file(self):
        token = Token.objects.get_or_create(user=self.base_user)[0]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.endpoints["export"]("xlsx"))

        self.assertEquals(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_cant_1000_requests_in_one_day(self):
        response = None

        token = Token.objects.get_or_create(user=self.base_user)[0]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        for _ in range(1001):
            response = self.client.get(self.endpoints["user"])

        self.assertEquals(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
