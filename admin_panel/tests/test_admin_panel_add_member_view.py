from django.urls import reverse
from django.contrib.messages import get_messages
from members.models import Member
from django.utils.timezone import localdate
from .base.test_base import TestBase

class AddMemberViewTests(TestBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        
        cls.form_data = {
            'email': 'testmember@example.com',
            'full_name': 'Test Member',
            'phone': '1234567890',
            'is_active': True,
            'payment_date': localdate(),
            'amount': 100.00
        }
        cls.members_url = reverse('admin_panel:members')
        cls.add_member_url = reverse('admin_panel:add_member')
        
    def test_add_member_requires_authentication(self):
        """Ensures authentication is required to access the "Add Member" view."""
        response = self.client.post(self.add_member_url, data=self.form_data)
        self.assertTrue(response.url.startswith(reverse('users:login_view')))

    def test_add_member_success(self):
        """Tests whether a member is added successfully when the data is valid."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        
        response = self.client.post(self.add_member_url, data=self.form_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.members_url)
        self.assertTrue(Member.objects.filter(email=self.form_data['email']).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Membro adicionado com sucesso!', [msg.message for msg in messages])

    def test_add_member_invalid_data(self):
        """Tests whether an error message is displayed when form data is invalid."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        
        self.form_data['email'] = 'invalid-email'
        response = self.client.post(self.add_member_url, data=self.form_data)

        self.assertRedirects(response, self.members_url)
        self.assertFalse(Member.objects.filter(full_name='Test Member').exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Erro ao adicionar o membro. Verifique os dados e tente novamente.', [msg.message for msg in messages])

    def test_add_member_not_post_method(self):
        """Tests whether the view redirects to the members page if the method is not POST."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.add_member_url)

        self.assertRedirects(response, self.members_url)

    def test_session_data_removed_on_success(self):
        """Tests whether session data is removed when the form is valid."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.post(self.add_member_url, data=self.form_data, follow=True)
        self.assertRedirects(response, self.members_url)
        session_data = self.client.session.get('form_data_add_member')
        self.assertIsNone(session_data, "Os dados da sessão não foram removidos após sucesso.")

    def test_add_member_unauthenticated_user(self):
        """Tests whether an unauthenticated user is redirected to the login page."""
        response = self.client.post(self.add_member_url)
        self.assertTrue(response.url.startswith(reverse('users:login_view')))
        
    def test_get_request_redirect(self):
        """Tests whether the GET request redirects to the members page."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.add_member_url)
        self.assertRedirects(response, self.members_url)