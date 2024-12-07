from django.test import TestCase
from django.contrib.auth import get_user_model
from faker import Faker
from django.urls import reverse

class TestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Configuração do Faker
        cls.faker = Faker('pt_BR')
        
        # Dados de CPF
        cls.valid_cpf = cls.faker.cpf().replace('.', '').replace('-', '')
        cls.invalid_cpf = '12345678901'
        
        # Dados do usuário
        cls.email = cls.faker.email()
        cls.full_name = cls.faker.name()
        cls.password = cls.faker.password(length=12, upper_case=True, special_chars=True, digits=True)
        
        # Dados para criação de um novo usuário
        cls.user_data = {
            'cpf': cls.valid_cpf,
            'email': cls.faker.email(domain='@exemple.com'),
            'full_name': cls.full_name,
            'password': cls.password,
        }
        
        # Criação de um usuário válido para testes de login
        cls.user = get_user_model().objects.create_user(
            cpf=cls.faker.cpf().replace('.', '').replace('-', ''),
            email=cls.email,
            password=cls.password
        )
        
        # URLs utilizadas nos testes
        cls.login_view_url = reverse('users:login_view')
        cls.login_submit_url = reverse('users:login_submit')
        cls.logout_url = reverse('users:logout_view')
        cls.admin_home_url = reverse('admin_panel:home')
