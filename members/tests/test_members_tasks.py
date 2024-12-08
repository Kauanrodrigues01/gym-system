from django.test import TestCase
from members.models import Member
from members.tasks import update_members_activity_status
from unittest.mock import patch, MagicMock
from ..tasks import send_billing_messages
from ..models import BillingMessage, Member

class CeleryTasksTest(TestCase):
    
    @patch('members.models.Member.update_activity_status')
    def test_update_members_activity_status_task(self, mock_update_status):
        """Tests the task for updating the activity status of members."""
    
        # Creates members with 'is_active=True' status
        member1 = Member.objects.create(full_name="Member 1", email="member1@example.com", is_active=True)
        member2 = Member.objects.create(full_name="Member 2", email="member2@example.com", is_active=True)
    
        # Executes the task
        update_members_activity_status()
    
        # Verifies that the update_activity_status method was called for both members
        self.assertEqual(mock_update_status.call_count, 2)  # Verifies it was called twice
    
        # Ensures that the mock was called. No need to check the arguments.
        mock_update_status.assert_any_call()

class SendBillingMessagesTaskTest(TestCase):

    def setUp(self):
        """
        Setup for tests: creates members and billing messages.
        """
        # Inactive members
        self.member1 = Member.objects.create(full_name='John Doe', is_active=False, email='john.doe@example.com')
        self.member2 = Member.objects.create(full_name='Jane Doe', is_active=False, email='jane.doe@example.com')

        # Billing messages
        self.message1 = BillingMessage.objects.create(member=self.member1, is_sent=False)
        self.message2 = BillingMessage.objects.create(member=self.member2, is_sent=False)

        # Already sent message
        self.sent_message = BillingMessage.objects.create(member=self.member1, is_sent=True)

    @patch('utils.ultramsg.UltraMsgAPI.send_message')  # Path to the UltraMsgAPI method
    def test_send_billing_messages_success(self, mock_send_message):
        """
        Tests if the task sends billing messages to inactive members.
        """
        # Creates a mocked response with 'status_code' and 'text' attributes
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'true'

        # Makes the mock return the simulated response
        mock_send_message.return_value = mock_response

        # Calls the task
        send_billing_messages()

        # Refreshes the objects in the database
        self.message1.refresh_from_db()
        self.message2.refresh_from_db()
        self.sent_message.refresh_from_db()

        # Verifies if the pending messages were sent
        self.assertTrue(self.message1.is_sent)
        self.assertTrue(self.message2.is_sent)

        # Verifies that already sent messages were not reprocessed
        self.assertTrue(self.sent_message.is_sent)

        # Verifies if the send_message method was called twice
        self.assertEqual(mock_send_message.call_count, 2)

    @patch('utils.ultramsg.UltraMsgAPI.send_message')  # Path to the UltraMsgAPI method
    def test_send_billing_messages_limit(self, mock_send_message):
        """
        Tests if the task processes at most 100 messages per execution.
        """
        BillingMessage.objects.all().delete()  # Clears all messages

        # Creates more than 100 pending billing messages
        BillingMessage.objects.bulk_create([
            BillingMessage(member=self.member1, is_sent=False) for _ in range(101)
        ])

        # Creates a mocked response with 'status_code' and 'text' attributes
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'true'

        # Makes the mock return the simulated response
        mock_send_message.return_value = mock_response

        # Calls the task
        send_billing_messages()

        # Verifies that the send_message method was called at most 100 times
        self.assertEqual(mock_send_message.call_count, 100)

        # Verifies that only 1 message remains unsent
        remaining_messages = BillingMessage.objects.filter(is_sent=False).count()
        self.assertEqual(remaining_messages, 1)

    @patch('utils.ultramsg.UltraMsgAPI.send_message')  # Path to the UltraMsgAPI method
    def test_no_messages_to_send(self, mock_send_message):
        """
        Tests if the task does nothing when there are no pending messages.
        """
        # Marks all messages as sent
        BillingMessage.objects.update(is_sent=True)

        # Creates a mocked response with 'status_code' and 'text' attributes
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'true'

        # Makes the mock return the simulated response
        mock_send_message.return_value = mock_response

        # Calls the task
        send_billing_messages()

        # Verifies that the send_message method was not called
        mock_send_message.assert_not_called()
