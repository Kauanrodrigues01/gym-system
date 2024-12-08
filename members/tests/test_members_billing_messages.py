from django.test import TestCase
from django.utils.timezone import localdate
from unittest.mock import patch
from datetime import timedelta
from ..models import Member, Payment, BillingMessage
from ..tasks import send_billing_messages, update_members_activity_status

class BillingMessageTests(TestCase):

    def setUp(self):
        # Create sample members and payments
        self.member_1 = Member.objects.create(
            email="member1@example.com",
            full_name="Member 1",
            phone="123456789",
            is_active=False
        )

        self.member_2 = Member.objects.create(
            email="member2@example.com",
            full_name="Member 2",
            phone="987654321",
            is_active=False
        )

        # Create a past payment to ensure the member becomes inactive
        Payment.objects.create(
            member=self.member_1,
            payment_date=localdate() - timedelta(days=31),  # Payment older than 30 days
            amount=100.00
        )

        # Create a past payment to ensure the member becomes inactive
        Payment.objects.create(
            member=self.member_2,
            payment_date=localdate() - timedelta(days=31),  # Payment older than 30 days
            amount=100.00
        )

    def test_billing_message_creation(self):
        """Test to verify the creation of billing messages for inactive members"""
        
        # Ensure that the BillingMessage is created for the inactive member
        self.member_1.update_activity_status()

        billing_message = BillingMessage.objects.filter(member=self.member_1).first()
        self.assertIsNotNone(billing_message)
        self.assertEqual(billing_message.is_sent, False)

    @patch('utils.ultramsg.UltraMsgAPI.send_message')
    def test_send_billing_message(self, mock_send_message):
        """Test to verify the sending of billing messages"""
        
        # Mock the message sending API to ensure it is called
        mock_send_message.return_value.status_code = 200
        mock_send_message.return_value.text = 'true'

        billing_message = BillingMessage.objects.create(
            member=self.member_2,
            is_sent=False
        )

        # Ensure the message is not actually sent during the test
        mock_send_message.assert_not_called()

        billing_message.send_message()
        
        # Verify if the status of the message was updated to sent
        billing_message.refresh_from_db()
        self.assertTrue(billing_message.is_sent)
        self.assertIsNotNone(billing_message.sent_at)
        self.assertEqual(billing_message.sent_at, localdate())

    @patch('utils.ultramsg.UltraMsgAPI.send_message')
    def test_no_duplicate_messages_sent(self, mock_send_message):
        """Test to ensure billing messages are not sent more than once within 30 days"""
        
        self.member_1.update_activity_status()

        # Create a BillingMessage for the inactive member inside the update_activity_status() method
        billing_message = BillingMessage.objects.filter(member=self.member_1).first()

        # Simulate sending the first message (without actually sending it)
        mock_send_message.return_value.status_code = 200
        mock_send_message.return_value.text = 'true'

        # Call send_message and update is_sent to True as it would be in a real scenario
        billing_message.send_message()  # This calls the actual method on the model
        self.assertTrue(billing_message.is_sent)

        # Try sending again and ensure the update_activity_status() method does not create a new message
        self.member_1.update_activity_status()
        
        messages = BillingMessage.objects.filter(member=self.member_1)
        
        # The second message should not be created
        self.assertEqual(messages.count(), 1)

    def test_no_billing_message_for_active_member(self):
        """Test to ensure no billing message is created for an active member"""
        BillingMessage.objects.all().delete()
        
        # Create a payment that ensures the member is active
        Payment.objects.create(
            member=self.member_1,
            payment_date=localdate(),  # Payment within the last 30 days
            amount=100.00
        )

        # Ensure that the BillingMessage is not created for the active member
        self.member_1.update_activity_status()

        billing_message = BillingMessage.objects.filter(member=self.member_1).first()
        self.assertIsNone(billing_message)

    @patch('utils.ultramsg.UltraMsgAPI.send_message')
    def test_billing_message_creation_with_updated_member_status(self, mock_send_message):
        """Test to verify billing message creation after member's status is updated"""
        
        mock_send_message.return_value.status_code = 200
        mock_send_message.return_value.text = 'true'

        # Create a payment that makes the member inactive
        Payment.objects.create(
            member=self.member_1,
            payment_date=localdate() - timedelta(days=31),  # Payment older than 30 days
            amount=100.00
        )

        # Update activity status and check message creation
        self.member_1.update_activity_status()
        billing_message = BillingMessage.objects.filter(member=self.member_1).first()
        
        self.assertIsNotNone(billing_message)
        self.assertFalse(billing_message.is_sent)
        self.assertIsNone(billing_message.sent_at)

    def test_billing_message_creation_for_multiple_inactive_members(self):
        """Test to ensure billing messages are created for multiple inactive members"""
        
        # Create multiple payments to mark members as inactive
        Payment.objects.create(
            member=self.member_1,
            payment_date=localdate() - timedelta(days=31),
            amount=100.00
        )
        
        Payment.objects.create(
            member=self.member_2,
            payment_date=localdate() - timedelta(days=31),
            amount=100.00
        )

        # Ensure both members have billing messages created
        self.member_1.update_activity_status()
        self.member_2.update_activity_status()

        billing_messages = BillingMessage.objects.filter(is_sent=False)
        self.assertEqual(billing_messages.count(), 2)
