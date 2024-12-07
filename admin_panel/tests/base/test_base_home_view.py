from members.models import Member, Payment
from django.utils.timezone import localdate
from django.urls import reverse
from .test_base import TestBase

class TestBaseHomeView(TestBase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        
        cls.home_url = reverse('admin_panel:home')
        cls.login_url = reverse('users:login_view')
        
        # Create reusable members
        cls.active_member = Member.objects.create(
            email=cls.faker.email(),
            full_name=cls.faker.name(),
            phone='85988888888',
            is_active=True
        )
        cls.inactive_member = Member.objects.create(
            email=cls.faker.email(),
            full_name=cls.faker.name(),
            phone='85966666666',
            is_active=False
        )
        
        # Create reusable payment
        cls.payment = Payment.objects.create(
            member=cls.active_member,
            payment_date=localdate(),
            amount=100
        )
        
    def create_member_inactive(self):
        return Member.objects.create(
            email=self.faker.email(),
            full_name=self.faker.name(),
            phone=self.faker.phone_number().replace(' ', '').replace('-', ''),
            is_active=False
        )
        
    def create_member_active(self):
        return Member.objects.create(
            email=self.faker.email(),
            full_name=self.faker.name(),
            phone=self.faker.phone_number().replace(' ', '').replace('-', ''),
            is_active=True
        )
        
    def create_payment(self, member=None, payment_date=localdate(), amount=100):
        if not isinstance(member, Member):
            member = self.active_member
            
        return Payment.objects.create(
            member=member,
            payment_date=payment_date,
            amount=amount
        )