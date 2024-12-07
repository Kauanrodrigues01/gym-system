from django.urls import reverse
from admin_panel.models import Member
from members.forms import MemberEditForm
from .base.test_base import TestBase


class EditMemberViewAndEditMemberTests(TestBase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        
        cls.member = Member.objects.create(
            email="member@example.com",
            full_name="Test Member",
            phone="123456789",
            is_active=True,
        )
        cls.edit_member_url = reverse("admin_panel:edit_member", kwargs={'id': cls.member.id})
        cls.edit_member_view_url = reverse("admin_panel:edit_member_view", kwargs={'id': cls.member.id})
        cls.valid_data = {
            "email": "updated@example.com",  
            "full_name": "Updated Member",  
            "phone": "9876543210", 
            "is_active": False, 
        }
        cls.invalid_data = {
            "email": "invalid-email",
            "full_name": "",
            "phone": "",
            "is_active": False,
        }
        
    def test_edit_member_view_requires_authentication(self):
        """Ensures authentication is required to access the "Edit Member View" view."""
        response = self.client.get(self.edit_member_view_url)
        self.assertTrue(response.url.startswith(reverse('users:login_view')))
    
    def test_edit_member_view_renders_correct_template(self):
        """Tests if the correct template is rendered for the Edit Member page."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.edit_member_view_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_panel/pages/member_edit.html")

    def test_edit_member_view_contains_form_and_member(self):
        """Tests if the form and member data are present in the context."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.edit_member_view_url)
        self.assertIsInstance(response.context["form"], MemberEditForm)
        self.assertEqual(response.context["member"], self.member)
        
    def test_edit_member_view_renders_form_with_instance_member(self):
        """Tests if the form contains the member instance data."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.edit_member_view_url)
        self.assertContains(response, self.member.email)
        self.assertContains(response, self.member.full_name)
        self.assertContains(response, self.member.phone)
        
    def test_edit_member_view_return_404_status_code_if_not_exists_member_with_id(self):
        """Ensures the view returns a 404 status code if the member ID does not exist."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(reverse("admin_panel:edit_member_view", kwargs={'id': 1000}))
        self.assertEqual(response.status_code, 404)
        
    def test_edit_member_view_loads_session_data(self):
        """Tests if session data is used to pre-populate the form."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        session_data = {
            'email': 'session@example.com',
            'full_name': 'Session Member',
            'phone': '111111111',
            'is_active': True
        }
        session = self.client.session
        session['form_data_edit_member'] = session_data
        session.save()

        response = self.client.get(self.edit_member_view_url)
        form = response.context['form']

        # Verifies if the form was populated with session data
        self.assertEqual(form.data['email'], session_data['email'])
        self.assertEqual(form.data['full_name'], session_data['full_name'])
        self.assertEqual(form.data['phone'], session_data['phone'])
        self.assertTrue(form.data['is_active'])

    def test_edit_member_requires_authentication(self):
        """Ensures authentication is required to access the "Edit Member" view."""
        response = self.client.post(self.edit_member_url, data=self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('users:login_view')))
        
    def test_redirects_to_members_on_get_request(self):
        """Tests if the view redirects to the members list when accessed with a GET request instead of POST."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.edit_member_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_panel:members'))
        
    def test_edit_member_successful_post(self):
        """Tests if editing a member works with valid data."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.post(self.edit_member_url, data=self.valid_data)
        
        member = Member.objects.get(id=self.member.id)
        self.assertEqual(member.email, self.valid_data['email'])
        self.assertEqual(member.full_name, self.valid_data['full_name'])
        self.assertEqual(member.phone, self.valid_data['phone'])
        self.assertFalse(member.is_active)
        self.assertRedirects(response, reverse("admin_panel:members"))

        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, 'Membro atualizado com sucesso!')

    def test_edit_member_invalid_post(self):
        """Tests if submitting invalid data returns appropriate errors."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.post(self.edit_member_url, data=self.invalid_data)
        
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, 'Erro ao atualizar o membro. Verifique os dados e tente novamente.')
        
        response = self.client.get(self.edit_member_view_url)
        form_errors = response.context['form'].errors
        self.assertIn('email', form_errors)
        self.assertIn('full_name', form_errors)
        self.assertIn('phone', form_errors)

    def test_edit_member_404_for_nonexistent_member(self):
        """Tests if accessing a non-existent member returns 404."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(reverse('admin_panel:edit_member', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_edit_member_session_data_persisted(self):
        """Tests if invalid form data is stored in the session."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.post(self.edit_member_url, data=self.invalid_data)
        session_data = response.wsgi_request.session.get("form_data_edit_member")
        self.assertIsNotNone(session_data)
        self.assertEqual(session_data["email"], "invalid-email")
        self.assertEqual(session_data["full_name"], "")
        self.assertEqual(session_data["phone"], "")

    def test_edit_member_clears_session_on_success(self):
        """Tests if session data is cleared after a successful submission."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        session = self.client.session
        session["form_data_edit_member"] = self.valid_data
        session.save()

        self.client.post(self.edit_member_url, data=self.valid_data)
        session_data = self.client.session.get("form_data_edit_member")
        self.assertIsNone(session_data)