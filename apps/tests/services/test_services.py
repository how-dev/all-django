from django.test import TestCase

from services.user_flow import CPFLogics


class FinalUserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cpf_logics = CPFLogics()
        cls.valid_cpf = "86450100206"
        cls.invalid_cpf = "86450100205"

    def test_can_validate_valid_cpf(self):
        validate_cpf = self.cpf_logics.validate_cpf
        self.assertEquals(validate_cpf(self.valid_cpf), True)

    def test_cant_validate_invalid_cpf(self):
        validate_cpf = self.cpf_logics.validate_cpf
        self.assertEquals(validate_cpf(self.invalid_cpf), False)
