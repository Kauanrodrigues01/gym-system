from datetime import timedelta, date, datetime
from django.test import TestCase
from django.utils.timezone import localdate
from parameterized import parameterized
from members.models import Member, Payment, BillingMessage
from django.core.exceptions import ValidationError
from unittest.mock import patch, MagicMock

class TestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Initial test setup."""
        cls.member = Member.objects.create(
            email="test@example.com",
            full_name="Test User",
            phone="123456789"
        )

class MemberModelTestCase(TestBase):

    def test_member_creation(self):
        """Tests member creation."""
        self.assertEqual(self.member.email, "test@example.com")
        self.assertEqual(self.member.full_name, "Test User")
        self.assertFalse(self.member.is_active)
        
    def test_member_str(self):
        """Tests the __str__ method of the Member model."""
        self.assertEqual(str(self.member), self.member.full_name)

    def test_last_payment_date_none(self):
        """Tests the last_payment_date property when there are no payments."""
        self.assertIsNone(self.member.last_payment_date)

    def test_last_payment_date(self):
        """Tests the last_payment_date property when payments exist."""
        Payment.objects.create(member=self.member, payment_date=localdate() - timedelta(days=5))
        Payment.objects.create(member=self.member, payment_date=localdate())
        self.assertEqual(self.member.last_payment_date, localdate())

    @parameterized.expand([
        (timedelta(days=15), True),  # Delta of 15 days -> should be active
        (timedelta(days=31), False),  # Delta of 31 days -> should be inactive
    ])
    def test_update_activity_status(self, delta_days, expected_status):
        """Tests the update_activity_status method with different payment intervals."""
        Payment.objects.create(member=self.member, payment_date=localdate() - delta_days)
        self.member.update_activity_status()
        self.assertEqual(self.member.is_active, expected_status)
        

class PaymentModelTestCase(TestBase):

    def test_payment_creation(self):
        """Tests payment creation."""
        payment = Payment.objects.create(member=self.member, amount=150.00)
        self.assertEqual(payment.member, self.member)
        self.assertEqual(payment.amount, 150.00)
        self.assertEqual(payment.payment_date, localdate())

    @parameterized.expand([
        (localdate(), True),  # Recent payment, member must be active
        (localdate() - timedelta(days=31), False),  # Payment older than 30 days, member must be inactive
    ])
    def test_payment_save_updates_member_status(self, payment_date, expected_status):
        """Tests if the payment save method updates the member status based on payment date."""
        member = Member.objects.create(email="teste@teste.com", full_name="Teste", phone="5585966667888", is_active=False)
        payment = Payment.objects.create(member=member, amount=100.00, payment_date=payment_date)
        
        member.refresh_from_db()
        self.assertEqual(member.is_active, expected_status)

        payment.delete()

    def test_payment_without_member(self):
        """Tests creating a payment without an associated member."""
        payment = Payment.objects.create(amount=100.00, payment_date=localdate())
        self.assertEqual(Payment.objects.all().count(), 1)
        self.assertTrue(Payment.objects.filter(id=payment.id))
    
    def test_payment_str(self):
        """Tests the __str__ method of the Payment model."""
        payment = Payment.objects.create(member=self.member, amount=100.00)
        self.assertEqual(str(payment), f"{self.member.full_name} | {payment.payment_date} | R$ {payment.amount}")

    def test_payment_str_no_member(self):
        """Tests the __str__ method of the Payment model when the member is deleted."""
        payment = Payment.objects.create(member=self.member, amount=100.00)
        self.member.delete()
        payment.refresh_from_db()
        self.assertEqual(
            str(payment), f"Pagamento sem aluno associado | {payment.payment_date} | R$ {payment.amount}"
        )

    @parameterized.expand([
        (1, 100.00),  # Month with payment
        (2, 0.00),  # Month without payment
    ])
    def test_get_monthly_profit(self, month, expected_total):
        """Tests calculating profits for a specific month."""
        if month == 1:
            Payment.objects.create(member=self.member, amount=100.00, payment_date=datetime(2024, 1, 1))
        total_profit = Payment.get_monthly_profit(month=month)
        self.assertEqual(total_profit, expected_total)

    def test_get_monthly_profit_invalid_month(self):
        """Tests behavior when an invalid month is passed."""
        with self.assertRaises(ValidationError):
            Payment.get_monthly_profit(month=13)

    def test_get_current_month_profit(self):
        """Tests calculating profits for the current month."""
        Payment.objects.create(member=self.member, amount=100.00, payment_date=localdate())
        Payment.objects.create(member=self.member, amount=200.00, payment_date=localdate())
        total_profit = Payment.get_current_month_profit()
        self.assertEqual(total_profit, 300.00)
        
        Payment.objects.create(member=self.member, amount=200.00, payment_date=localdate())
        total_profit = Payment.get_current_month_profit()
        self.assertEqual(total_profit, 500.00)

    def test_get_current_year_profit(self):
        """Tests calculating profits for the current year."""
        current_year = localdate().year
        january_date = date(current_year, 1, 10)
        july_date = date(current_year, 7, 10)
        
        Payment.objects.create(member=self.member, amount=100.00, payment_date=january_date)
        Payment.objects.create(member=self.member, amount=200.00, payment_date=july_date)
        
        total_profit = Payment.get_current_year_profit()
        self.assertEqual(total_profit, 300.00)

class BillingMessageModelTest(TestCase):

    def setUp(self):
        """
        Setup for tests: creates a member and a billing message.
        """
        # Creates a member for testing
        self.member = Member.objects.create(full_name='John Doe', is_active=False, email='john.doe@example.com')

        # Creates a billing message for this member
        self.billing_message = BillingMessage.objects.create(member=self.member, is_sent=False)

    def test_billing_message_creation(self):
        """
        Tests if the BillingMessage object is created correctly.
        """
        # Verifies if the billing message was created
        self.assertEqual(self.billing_message.member, self.member)
        self.assertFalse(self.billing_message.is_sent)
        self.assertIsNone(self.billing_message.sent_at)

    @patch('utils.ultramsg.UltraMsgAPI.send_message')  # Path to the UltraMsgAPI method
    def test_send_message_success(self, mock_send_message):
        """
        Tests if the send_message method correctly updates is_sent and sent_at when successful.
        """
        # Mocking the response from the UltraMsg API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'true'

        # Makes the mock return the simulated response
        mock_send_message.return_value = mock_response

        # Calls the send_message method
        self.billing_message.send_message()

        # Verifies if the message was sent successfully
        self.assertTrue(self.billing_message.is_sent)
        self.assertEqual(self.billing_message.sent_at, date.today())  # Verifies if the sent_at date is today's date

    @patch('utils.ultramsg.UltraMsgAPI.send_message')  # Path to the UltraMsgAPI method
    def test_send_message_failure(self, mock_send_message):
        """
        Tests if the send_message method handles failures correctly and doesn't update is_sent.
        """
        # Mocking a failed response from the UltraMsg API
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'error'

        # Makes the mock return the simulated response
        mock_send_message.return_value = mock_response

        # Calls the send_message method
        self.billing_message.send_message()

        # Verifies if the message wasn't marked as sent
        self.assertFalse(self.billing_message.is_sent)
        self.assertIsNone(self.billing_message.sent_at)

    def test_str_method(self):
        """
        Tests the string representation of the BillingMessage model.
        """
        # Verifies if the string representation of the BillingMessage is correct
        expected_str = f"BillingMessage for {self.member.full_name} - Sent: {self.billing_message.is_sent}"
        self.assertEqual(str(self.billing_message), expected_str)

    def test_indexes(self):
        """
        Tests if the indexes on 'is_sent' and 'sent_at' fields are created properly.
        """
        # Verifies that the model's indexes are created as expected
        self.assertTrue(BillingMessage._meta.indexes[0].fields, ['is_sent'])
        self.assertTrue(BillingMessage._meta.indexes[1].fields, ['sent_at'])
