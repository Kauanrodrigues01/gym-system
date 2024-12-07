from django.urls import reverse
from django.contrib.messages import get_messages
from members.models import Member, Payment
from members.forms import PaymentForm
from .base.test_base import TestBase

class AddPaymentTests(TestBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        
        cls.member = Member.objects.create(
            full_name="Test Member",
            email="test@example.com",
            phone="123456789",
            start_date="2024-01-01",
            is_active=True,
        )
        cls.valid_payment_data = {"payment_date": "2024-11-22", "amount": 100.00}
        cls.invalid_payment_data = {"payment_date": "", "amount": ""}
        cls.add_payment_view_url = reverse("admin_panel:add_payment_view", kwargs={"id": cls.member.id})
        cls.add_payment_url = reverse("admin_panel:add_payment", kwargs={"id": cls.member.id})
        
    def test_add_payment_view_redirect_if_not_logged_in(self):
        """Tests redirection to login page for unauthenticated users on GET request."""
        response = self.client.get(self.add_payment_view_url)
        self.assertRedirects(response, f"{reverse('users:login_view')}?next={self.add_payment_view_url}")

    def test_add_payment_view_status_code(self):
        """Tests if the add_payment_view returns status code 200."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.add_payment_view_url)
        self.assertEqual(response.status_code, 200)

    def test_add_payment_view_template_used(self):
        """Tests if the correct template is used for add_payment_view."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.add_payment_view_url)
        self.assertTemplateUsed(response, "admin_panel/pages/add_payment.html")
        
    def test_add_payment_view_template_form_fields(self):
        """Ensure all form fields are rendered in the template."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.add_payment_view_url)

        for field_name in ['payment_date', 'amount']:
            self.assertContains(response, f'name="{field_name}"')
            
    def test_add_payment_view_template_validation_errors(self):
        """Test if validation errors are displayed on the template."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.post(self.add_payment_url, data=self.invalid_payment_data)

        self.assertRedirects(response, self.add_payment_view_url)
        response = self.client.get(self.add_payment_view_url)
        
        content = response.content.decode('utf-8')

        for _ in self.invalid_payment_data.keys():
            self.assertIn(f'Este campo é obrigatório.', content)

    def test_add_payment_view_context_contains_form(self):
        """Tests if the form is included in the context of add_payment_view."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.add_payment_view_url)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], PaymentForm)

    def test_add_payment_view_context_contains_member(self):
        """Tests if the member is included in the context of add_payment_view."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.add_payment_view_url)
        self.assertIn("member", response.context)
        self.assertEqual(response.context["member"], self.member)

    def test_add_payment_view_contains_member_name(self):
        """Tests if the member's full name is rendered in the response."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.add_payment_view_url)
        self.assertContains(response, self.member.full_name)


    def test_add_payment_view_invalid_member(self):
        """Tests add_payment_view with invalid member ID."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        invalid_url = reverse("admin_panel:add_payment_view", kwargs={"id": 999})
        response = self.client.get(invalid_url)
        
        self.assertEqual(response.status_code, 404)
        
    def test_add_payment_redirect_if_not_logged_in_on_post(self):
        """Tests redirection to login page for unauthenticated users on POST request."""
        response = self.client.post(self.add_payment_url, data=self.valid_payment_data)
        self.assertRedirects(response, f"{reverse('users:login_view')}?next={self.add_payment_url}")
        
    def test_add_payment_redirect_if_request_is_not_post(self):
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.add_payment_url)
        self.assertRedirects(response, self.add_payment_view_url)

    def test_add_payment_post_valid_data(self):
        """Tests POST request to add_payment with valid data."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.post(self.add_payment_url, data=self.valid_payment_data)
        
        self.assertRedirects(response, reverse('admin_panel:members'))
        self.assertTrue(Payment.objects.filter(member=self.member).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Pagamento adicionado com sucesso!', [msg.message for msg in messages])

    def test_add_payment_post_invalid_data(self):
        """Tests POST request to add_payment with invalid data."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.post(self.add_payment_url, data=self.invalid_payment_data)
        
        self.assertRedirects(response, self.add_payment_view_url)
        self.assertFalse(Payment.objects.filter(member=self.member).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Erro ao adicionar pagamento. Verifique os dados e tente novamente.', [msg.message for msg in messages])

    def test_add_payment_view_form_data_session(self):
        """Tests if session data is passed to the form on add_payment_view."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        session = self.client.session
        session["form_data_add_payment"] = self.valid_payment_data
        session.save()

        response = self.client.get(self.add_payment_view_url)
        
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form.data['payment_date'], '2024-11-22')
        self.assertEqual(form.data['amount'], 100.0)
        
    def test_add_payment_success_clears_session(self):
        """Ensure session data is cleared after a successful payment."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        session = self.client.session
        session["form_data_add_payment"] = self.valid_payment_data
        session.save()

        response = self.client.post(self.add_payment_url, data=self.valid_payment_data)
        self.assertRedirects(response, reverse("admin_panel:members"))

        session = self.client.session
        self.assertNotIn("form_data_add_payment", session)

    def test_add_payment_invalid_member(self):
        """Tests add_payment with invalid member ID."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        invalid_url = reverse("admin_panel:add_payment", kwargs={"id": 999})
        response = self.client.post(invalid_url, data=self.valid_payment_data)
        
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Payment.objects.filter(payment_date="2024-11-22", amount=100.00).exists())
