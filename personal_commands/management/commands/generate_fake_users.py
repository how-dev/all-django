from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from faker import Faker

from apps.login_logic.models import FinalUserModel

fake = Faker()


class Command(BaseCommand):
    help = "Print Hello World"

    def add_arguments(self, parser):
        parser.add_argument("qtd", type=int)

    @staticmethod
    def handle(*_, **options):
        qtd = options["qtd"]

        for _ in range(qtd):
            password = make_password(".")
            try:
                FinalUserModel.objects.create(
                    name=fake.name(),
                    email=fake.unique.email(),
                    password=str(password),
                    is_active=True,
                )
            except Exception as e:
                print(e)
                continue
