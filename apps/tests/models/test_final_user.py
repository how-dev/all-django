from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.utils import timezone

from apps.login_logic.models import FinalUserModel

from faker import Faker

fake = Faker()


class FinalUserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.base_user = FinalUserModel.objects.create(
            name=fake.name(),
            email=fake.unique.email(),
            password=make_password(fake.name()),
            is_active=True,
            date_joined=timezone.now(),
            last_login=timezone.now(),
            document="00000000000",
        )

    def test_final_user_model_hasnt_default_fields(self):
        self.assertIsInstance(self.base_user.username, type(None))
        self.assertIsInstance(self.base_user.user_permissions, type(None))
        self.assertIsInstance(self.base_user.first_name, type(None))
        self.assertIsInstance(self.base_user.last_name, type(None))
        self.assertIsInstance(self.base_user.groups, type(None))
        self.assertIsInstance(self.base_user.is_superuser, type(None))
        self.assertIsInstance(self.base_user.is_staff, type(None))

    def test_final_user_model_has_information_fields(self):
        self.assertIsInstance(self.base_user.name, str)
        self.assertIsInstance(self.base_user.email, str)
        self.assertIsInstance(self.base_user.password, str)
        self.assertIsInstance(self.base_user.is_active, bool)
        self.assertIsInstance(self.base_user.document, str)

    def test_final_user_model_has_datetime_fields(self):
        self.assertIsInstance(self.base_user.date_joined, datetime)
        self.assertIsInstance(self.base_user.last_login, datetime)
