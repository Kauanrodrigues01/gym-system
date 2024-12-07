from django.test import TestCase
from datetime import timedelta
from members.models import Member, Payment
from django.utils.timezone import localdate
from unittest.mock import patch


class MemberSignalsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member_data = {
            'email': 'teste@teste.com',
            'full_name': 'Aluno Teste',
            'phone': '5585966667843',
            'is_active': True
        }

    @patch('admin_panel.models.ActivityLog.objects.create')
    def test_member_creation_signal(self, mock_create):
        """Tests that creating a Member triggers the signal to log the creation in ActivityLog."""
        member = Member.objects.create(**self.member_data)
        self.assertEqual(mock_create.call_count, 1)
        self.assertIn(f'{member.full_name} foi cadastrado', mock_create.call_args[1]['description'])

    @patch('admin_panel.models.ActivityLog.objects.create')
    def test_member_update_signal(self, mock_create):
        """Tests that updating a Member triggers the signal to log the update in ActivityLog."""
        member = Member.objects.create(**self.member_data)
        member.full_name = 'Aluno Teste Atualizado'
        member.save()
        self.assertEqual(mock_create.call_count, 2)
        self.assertIn(f'{member.full_name} foi atualizado', mock_create.call_args[1]['description'])

    @patch('admin_panel.models.ActivityLog.objects.create')
    def test_member_delete_signal(self, mock_create):
        """Tests that deleting a Member triggers the signal to log the deletion in ActivityLog."""
        member = Member.objects.create(**self.member_data)
        member.delete()
        self.assertEqual(mock_create.call_count, 2)
        self.assertIn(f'{member.full_name} foi excluído', mock_create.call_args[1]['description'])


class PaymentSignalsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.member = Member.objects.create(
            email='teste@teste.com',
            full_name='Aluno Teste',
            phone='5585966667843',
            is_active=True
        )
        cls.payment_data = {
            'payment_date': localdate(),
            'amount': 100.00
        }
        cls.payment_update = Payment.objects.create(member=cls.member, **cls.payment_data)

    @patch('admin_panel.models.ActivityLog.objects.create')
    @patch('members.models.Member.update_activity_status')
    def test_payment_creation_signal(self, mock_update_status, mock_create):
        """
        Tests that creating a Payment calls update_activity_status and logs 
        the payment in ActivityLog.
        """
        Payment.objects.create(member=self.member, **self.payment_data)
        mock_update_status.assert_called_once()
        self.assertEqual(mock_create.call_count, 1)
        self.assertIn('realizou um pagamento de R$ 100.0', mock_create.call_args[1]['description'])

    @patch('admin_panel.models.ActivityLog.objects.create')
    def test_payment_without_member(self, mock_create):
        """Tests that creating a Payment without an associated Member logs the payment correctly in ActivityLog."""
        Payment.objects.create(amount=100.00, payment_date=localdate())
        self.assertEqual(mock_create.call_count, 1)
        self.assertIn('Pagamento sem aluno associado | realizou um pagamento de R$ 100.0', mock_create.call_args[1]['description'])

    @patch('admin_panel.models.ActivityLog.objects.create')
    @patch('members.models.Member.update_activity_status')
    def test_payment_update_signal(self, mock_update_status, mock_create):
        """
        Tests that updating a Payment does not log in ActivityLog, 
        but calls update_activity_status for the Member.
        """
        # Update a payment field (e.g., payment_date)
        self.payment_update.payment_date = localdate() - timedelta(days=1)
        self.payment_update.save()  # Triggers post_save, but `created` will be False
        
        # Ensure no ActivityLog is created for the Payment update
        mock_create.assert_not_called()

        # Ensure Member's activity status update is called
        mock_update_status.assert_called_once()
