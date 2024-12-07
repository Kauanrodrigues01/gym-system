from django.test import TestCase
from unittest.mock import patch
from members.models import Member
from members.tasks import update_members_activity_status

class CeleryTasksTest(TestCase):
    
    @patch('members.models.Member.update_activity_status')
    def test_update_members_activity_status_task(self, mock_update_status):
        """Testa a task de atualização de status dos membros."""
    
        # Cria membros com status 'is_active=True'
        member1 = Member.objects.create(full_name="Membro 1", email="membro1@example.com", is_active=True)
        member2 = Member.objects.create(full_name="Membro 2", email="membro2@example.com", is_active=True)
    
        # Executa a task
        update_members_activity_status()
    
        # Verifica se o método update_activity_status foi chamado para os dois membros
        self.assertEqual(mock_update_status.call_count, 2)  # Verifica que foi chamado duas vezes
    
        # Apenas garante que o mock foi chamado. Não precisa verificar os argumentos.
        mock_update_status.assert_any_call()
