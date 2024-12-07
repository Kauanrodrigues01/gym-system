from django.test import TestCase
from users.models import User
from faker import Faker

class TestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the entire TestCase
        cls.faker = Faker('pt_BR')

        cls.password = cls.faker.password(length=12, upper_case=True, special_chars=True, digits=True)

        cls.user = User.objects.create_user(
            cpf=cls.faker.cpf().replace('.', '').replace('-', ''),
            email=cls.faker.email(),
            password=cls.password
        )