from django.test import TestCase
from django.utils.timezone import localdate
from members.forms import MemberPaymentForm, MemberEditForm, PaymentForm
from members.models import Member, Payment
from faker import Faker


class BaseTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Instância do Faker adicionada ao setup
        cls.fake = Faker('pt_BR')
        
        # Dados compartilhados entre os testes
        cls.member_data = {
            'email': cls.fake.email(),
            'full_name': cls.fake.name(),
            'phone': '5585966667979',
            'is_active': True,
            'payment_date': localdate(),
            'amount': 100.0
        }
        
        cls.member = Member.objects.create(
            email=cls.fake.email(),
            full_name=cls.fake.name(),
            phone='5585966667843',
            is_active=True
        )
        
        cls.payment_data = {
            'payment_date': localdate(),
            'amount': 100.0
        }
