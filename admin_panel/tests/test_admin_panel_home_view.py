from django.utils.timezone import localdate
from django.utils.timezone import localtime
from admin_panel.models import ActivityLog
from .base.test_base_home_view import TestBaseHomeView


class TestHomeView(TestBaseHomeView):
    """Test cases for the Home view."""
    
    def test_home_view_renders_the_correct_template(self):
        """Tests if the home view renders the correct template."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.home_url)
        self.assertTemplateUsed(response, 'admin_panel/pages/home.html')
        
    def test_home_view_requires_authentication(self):
        """Tests if authentication is required to access the home view."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))
        
    def test_home_view_responds_for_authenticated_user(self):
        """Tests if an authenticated user can access the home view."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        
    def test_home_view_context_data(self):
        """Tests if the home view returns the correct context data."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.home_url)
        
        self.assertIn('count_members_actives', response.context)
        self.assertIn('count_members_inactives', response.context)
        self.assertIn('count_new_members_in_month', response.context)
        self.assertIn('profit_total_month', response.context)
        self.assertIn('recent_activities', response.context)
    
    def test_count_members_in_context(self):
        """Tests the count of active and inactive members in the context."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.home_url)
        
        self.assertEqual(response.context['count_members_actives'], 1)
        self.assertEqual(response.context['count_members_inactives'], 1)
        
    def test_count_new_members_in_month_context(self):
        """Tests the count of new members in the current month in the context."""
        # Modify reusable member to simulate creation in a different month
        self.inactive_member.created_at = localdate().replace(month=localdate().month - 1)
        self.inactive_member.save()
        
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.home_url)
        
        self.assertEqual(response.context['count_new_members_in_month'], 1)
        
    def test_profit_total_month_context(self):
        """Tests the total profit for the current month in the context."""
        payment1 = self.create_payment(member=self.active_member, payment_date=localdate())
        self.create_payment(member=self.active_member, payment_date=localdate().replace(month=localdate().month - 1))
        
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.home_url)
        
        self.assertEqual(response.context['profit_total_month'],(payment1.amount + self.payment.amount))
        
    def test_recent_activities_in_context(self):
        """Tests the recent activities in the context."""
        ActivityLog.objects.create(member=self.active_member, description="Test activity 1")
        ActivityLog.objects.create(member=self.active_member, description="Test activity 2")
        
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.home_url)
        
        # There are 6, including activity logs that are automatically saved when creating members and payments, due to the sign
        self.assertEqual(len(response.context['recent_activities']), 6)
        self.assertEqual(response.context['recent_activities'][0].description, "Test activity 2") # it is in position 0 because of order_by('-id')

    
    def test_renders_count_members_actives(self):
        """Tests if the count of active members is rendered correctly."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.home_url)
        self.assertContains(response, f"<p class=\"count\">{response.context['count_members_actives']}</p>")
        
    def test_renders_count_members_inactives(self):
        """Tests if the count of inactive members is rendered correctly."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.home_url)
        self.assertContains(response, f"<p class=\"count\">{response.context['count_members_inactives']}</p>")
        
    def test_renders_profit_total_month(self):
        """Tests if the total profit for the current month is rendered correctly."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.home_url)
        self.assertContains(response, f"<p class=\"count\">R$ {str(response.context['profit_total_month']).replace('.', ',')}</p>")
        
    def test_renders_count_new_members_in_month(self):
        """Tests if the count of new members in the current month is rendered correctly."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.home_url)
        self.assertContains(response, f"<p class=\"count\">{response.context['count_new_members_in_month']}</p>")
        
    def test_renders_recent_activities(self):
        """Tests if recent activities are rendered correctly."""
        ActivityLog.objects.create(member=self.active_member, description="Test activity 1")
        ActivityLog.objects.create(member=self.active_member, description="Test activity 2")
        
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.home_url)
        content = response.content.decode('utf-8')
        
        recent_activities = response.context['recent_activities']
        for activity in recent_activities:
            self.assertIn(activity.description, content)
            self.assertIn(localtime(activity.created_at).strftime("%d/%m/%y %H:%M"), content)
        
    def test_renders_no_recent_activities_message(self):
        """Tests if a message is displayed when there are no recent activities."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        ActivityLog.objects.all().delete()
        
        response = self.client.get(self.home_url)
        self.assertContains(response, "Não há atividades recentes.")
    
    def test_recent_activities_order(self):
        """Tests if recent activities are ordered by the most recent."""
        ActivityLog.objects.create(member=self.active_member, description="Old activity", created_at="2024-11-20")
        ActivityLog.objects.create(member=self.active_member, description="Recent activity", created_at="2024-11-21")
        
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.home_url)
        recent_activities = response.context['recent_activities']
        
        self.assertEqual(recent_activities[0].description, "Recent activity")
        self.assertEqual(recent_activities[1].description, "Old activity")