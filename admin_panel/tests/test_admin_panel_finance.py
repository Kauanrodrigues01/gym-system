from django.urls import reverse
from admin_panel.models import Payment, Member
from django.utils.timezone import localdate
from parameterized import parameterized
from .base.test_base import TestBase

class FinanceViewTest(TestBase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        
        # Create a member
        cls.member = Member.objects.create(
            email="member@example.com",
            full_name="John Doe",
            phone="123456789",
            start_date=localdate(),
            is_active=True
        )

        today = localdate()
        payments = []
        for month in range(1, 13):
            payment_date = today.replace(month=month, day=1)
            amount = month * 50  # 50, 100, 150, ..., 600
            payments.append(Payment(member=cls.member, payment_date=payment_date, amount=amount))

        Payment.objects.bulk_create(payments)

        cls.finance_url = reverse('admin_panel:finance')

    def test_finance_view_requires_authentication(self):
        response = self.client.get(self.finance_url)
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(response.url.startswith(reverse('users:login_view')))

    def test_finance_view_renders_correctly(self):
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.finance_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('current_year_profit', response.context)
        self.assertIn('current_month_profit', response.context)
        self.assertIn('months_profit', response.context)
        self.assertIn('month_with_highest_profit', response.context)
        self.assertIn('recents_payments', response.context)
        self.assertIn('graph_html', response.context)

    def test_finance_view_current_year_profit(self):
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.finance_url)
        self.assertEqual(response.context['current_year_profit'], sum(range(50, 650, 50)))

    def test_finance_view_current_month_profit(self):
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.finance_url)
        current_month_amount = localdate().month * 50
        self.assertEqual(response.context['current_month_profit'], current_month_amount)
        
    @parameterized.expand([
        ('Janeiro',), ('Fevereiro',), ('Março',), ('Abril',), 
        ('Maio',), ('Junho',), ('Julho',), ('Agosto',),
        ('Setembro',), ('Outubro',), ('Novembro',), ('Dezembro',)
    ])
    def test_month_in_context(self, month):
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.finance_url)
        months_profit = response.context['months_profit']
        
        self.assertIn(month, months_profit)

    def test_finance_view_month_with_highest_profit(self):
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.finance_url)
        highest_month = 12
        month_names = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        self.assertEqual(response.context['month_with_highest_profit'], month_names[highest_month - 1])

    def test_finance_view_recent_payments(self):
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.finance_url)
        recent_payments = response.context['recents_payments']
        self.assertEqual(recent_payments.count(), 12)
        self.assertQuerySetEqual(
            recent_payments,
            Payment.objects.order_by('-payment_date')[:12],
            transform=lambda x: x
        )

    @parameterized.expand([
        ('Lucro Total do Ano', f'R$ {sum(range(50, 650, 50))}'),
        ('Lucro do Mês atual', f'R$ {localdate().month * 50}'),
        ('Mês com Maior Lucro', 'Dezembro'),
    ])
    def test_dashboard_cards_display_correct_data(self, card_title, expected_value):
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.finance_url)
        html = response.content.decode()

        self.assertIn(card_title, html)
        self.assertIn(expected_value, html)


    def test_finance_view_download_links(self):
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.finance_url)
        html = response.content.decode()
        self.assertIn(reverse('admin_panel:generate_pdf_general_report'), html)
        self.assertIn(reverse('admin_panel:generate_pdf_report_of_current_day'), html)

    @parameterized.expand([
        ('January', '50,00'),
        ('February','100,00'),
        ('March', '150,00'),
        ('April', '200,00'),
        ('May', '250,00'),
        ('June', '300,00'),
        ('July', '350,00'),
        ('August', '400,00'),
        ('September', '450,00'),
        ('October', '500,00'),
        ('November', '550,00'),
        ('December', '600,00'),
    ])
    def test_monthly_profit_list_contains_correct_data(self, month, profit):
        """
        Testa se cada mês e seu lucro esperado estão presentes na lista <ul>.
        """
        months_in_portuguese = {
            'January': 'Janeiro',
            'February': 'Fevereiro',
            'March': 'Março',
            'April': 'Abril',
            'May': 'Maio',
            'June': 'Junho',
            'July': 'Julho',
            'August': 'Agosto',
            'September': 'Setembro',
            'October': 'Outubro',
            'November': 'Novembro',
            'December': 'Dezembro',
        }
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.finance_url)
        html = response.content.decode('utf-8')

        expected_li = f"<li>{months_in_portuguese[month]} | R$ {profit}</li>"
        self.assertIn(expected_li, html)
        
    @parameterized.expand([
        ('Janeiro', 50), ('Fevereiro', 100), ('Março', 150), ('Abril', 200),
        ('Maio', 250), ('Junho', 300), ('Julho', 350), ('Agosto', 400),
        ('Setembro', 450), ('Outubro', 500), ('Novembro', 550), ('Dezembro', 600)
    ])
    def test_finance_view_graph_contains_correct_data(self, month, profit):
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.finance_url)
        graph_html = response.context['graph_html']

        self.assertIn('Lucro Mensal', graph_html)
        if month != 'Março':
            self.assertIn(month, graph_html)
        self.assertIn(str(profit), graph_html)