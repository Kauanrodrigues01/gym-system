from django.urls import reverse
from admin_panel.models import Member
from .base.test_base import TestBase

class DeleteMemberViewTests(TestBase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        
        cls.member = Member.objects.create(
            email="member@example.com",
            full_name="Test Member",
            phone="123456789",
            is_active=True,
        )
        cls.delete_member_url = reverse('admin_panel:delete_member', kwargs={'id': cls.member.id})

    def test_delete_member_requires_authentication(self):
        """Tests if authentication is required to delete a member."""
        response = self.client.get(self.delete_member_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('users:login_view')))

    def test_delete_member_successful(self):
        """Tests if a member is successfully deleted."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.delete_member_url)
        self.assertRedirects(response, reverse('admin_panel:members'))
        self.assertFalse(Member.objects.filter(id=self.member.id).exists())

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, 'Membro deletado com sucesso!')

    def test_delete_member_404_for_nonexistent_member(self):
        """Tests if trying to delete a nonexistent member returns a 404 error."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(reverse('admin_panel:delete_member', kwargs={'id': 999}))
        self.assertEqual(response.status_code, 404)

    def test_delete_member_does_not_delete_other_members(self):
        """Tests if only the targeted member is deleted."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        other_member = Member.objects.create(
            email="other@example.com",
            full_name="Other Member",
            phone="987654321",
            is_active=True,
        )
        response = self.client.get(self.delete_member_url)
        self.assertRedirects(response, reverse('admin_panel:members'))
        self.assertFalse(Member.objects.filter(id=self.member.id).exists())
        self.assertTrue(Member.objects.filter(id=other_member.id).exists())
