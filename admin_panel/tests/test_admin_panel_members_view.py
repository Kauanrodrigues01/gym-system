from django.urls import reverse
from django.utils.timezone import localdate
from members.models import Member, Payment
from datetime import timedelta
from .base.test_base import TestBase

class TestMembersView(TestBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        
        # Criar alguns membros para os testes
        cls.member1 = Member.objects.create(
            full_name='John Doe',
            email='john@example.com',
            phone='123456789',
            is_active=True,
            start_date=localdate() - timedelta(days=30)
        )
        
        cls.member2 = Member.objects.create(
            full_name='Jane Smith',
            email='jane@example.com',
            phone='987654321',
            is_active=False,
            start_date=localdate() - timedelta(days=60)
        )

        # Criar pagamentos para os membros
        cls.payment_member1 = Payment.objects.create(member=cls.member1, payment_date=localdate() - timedelta(days=10), amount=100)
        cls.payment_member2 = Payment.objects.create(member=cls.member2, payment_date=localdate() - timedelta(days=40), amount=100)

        cls.members_url = reverse('admin_panel:members')
        cls.login_url = reverse('users:login_view')

    def test_authenticated_user_can_access_page(self):
        """Test if authenticated user can access the members page."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.members_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/pages/members.html')
    
    def test_unauthenticated_user_redirected(self):
        """Test if unauthenticated user is redirected to login."""
        response = self.client.get(self.members_url)
        self.assertTrue(response.url.startswith(self.login_url))

    def test_search_filter(self):
        """Test search functionality for filtering members."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.members_url, {'q': 'John'})
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.member1.full_name, content)
        self.assertNotIn(self.member2.full_name, content)

    def test_status_filter(self):
        """Test filtering members by active/inactive status."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        
        # Test active members
        response = self.client.get(self.members_url, {'status': 'active'})
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.member1.full_name, content)
        self.assertNotIn(self.member2.full_name, content)
        
        # Test inactive members
        response = self.client.get(self.members_url, {'status': 'inactive'})
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.member2.full_name, content)
        self.assertNotIn(self.member1.full_name, content)

    def test_payment_date_filter(self):
        """Test filtering members by payment date."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.members_url, {'last_payment': self.payment_member1.payment_date})
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.member1.full_name, content)
        self.assertNotIn(self.member2.full_name, content)

    def test_pagination(self):
        """Test pagination with a large number of members."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        
        # Create more members to test pagination
        for i in range(20, 31):
            Member.objects.create(
                full_name=f'Member {i}',
                email=f'member{i}@example.com',
                phone=f'1234567{i}',
                is_active=True,
                start_date=localdate() - timedelta(days=i)
            )
        
        response = self.client.get(self.members_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1')  # Check if page 1 is displayed
        self.assertContains(response, '2')  # Check if page 2 is displayed
        
        # Check members on page 1
        for i in range(20, 31):
            self.assertContains(response, f'Member {i}')
        
    def test_context_data(self):
        """Test context data returned by the view."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.members_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('members', response.context)
        self.assertIn('pagination_range', response.context)
        self.assertIn('search_query', response.context)
        self.assertIn('form', response.context)

    def test_no_members_found(self):
        """Test view behavior when no members are found."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.members_url, {'q': 'Nonexistent Name'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhum aluno encontrado.')

    def test_edge_case_with_few_members(self):
        """Test behavior when there are few members (less than one page)."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        
        # Create 5 members
        for i in range(1, 6):
            Member.objects.create(
                full_name=f'Member {i}',
                email=f'member{i}@example.com',
                phone=f'1234567{i}',
                is_active=True,
                start_date=localdate() - timedelta(days=i)
            )

        response = self.client.get(self.members_url)
        self.assertEqual(response.status_code, 200)
        
        # Verify all members are on the page, no pagination needed
        for i in range(1, 6):
            self.assertContains(response, f'Member {i}')
        
        # Verify no links for additional pages
        self.assertNotContains(response, 'Next')
        self.assertNotContains(response, 'Previous')

    def test_no_results_for_filter(self):
        """Test behavior when a filter returns no results."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        self.member1.delete()
        
        response = self.client.get(self.members_url, {'status': 'active'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhum aluno encontrado.')
        
    def test_form_add_member(self):
        """Test if the member addition form is displayed."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        
        response = self.client.get(self.members_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
    def test_whether_the_register_payment_button_appears_when_a_student_is_inactive(self):
        """Tests whether the register payment button appears if the student is inactive"""
        self.member1.delete()
        self.client.login(cpf=self.user.cpf, password=self.password)
        
        response = self.client.get(self.members_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<a href="{reverse('admin_panel:add_payment_view', kwargs={'id': self.member2.id}) }" class="btn btn-add">Registrar pagamento</a>')
    
    def test_if_the_register_payment_button_does_not_appear_when_a_student_is_active(self):
        """Tests whether the registration payment button does not appear if the student is active"""
        self.member2.delete()
        self.client.login(cpf=self.user.cpf, password=self.password)
        
        response = self.client.get(self.members_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, f'<a href="{reverse('admin_panel:add_payment_view', kwargs={'id': self.member1.id}) }" class="btn btn-add">Registrar pagamento</a>')
