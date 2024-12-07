from django.utils.timezone import localdate
from admin_panel.models import DailyReport
from members.models import Member, Payment
from unittest.mock import patch
from .base.test_base_report_views import TestBaseReportViews

class GeneratePDFGeneralReportTestCase(TestBaseReportViews):
    
    def test_requires_authentication(self):
        # Ensure only authenticated users can access the view
        response = self.client.get(self.general_report_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertIn('/users/login/', response.url)

    def test_authenticated_access(self):
        # Log in and test access
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.general_report_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename=gym_report_'))

    def test_context_data(self):
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.general_report_url)

        self.assertEqual(response.status_code, 200)
        pdf_content = self.extract_text_from_pdf(response.content)

        # Verify content in the PDF
        self.assertIn('R$150,00', pdf_content)  # Total revenue
        self.assertIn('Alunos Ativos: 1', pdf_content)
        self.assertIn('Alunos Pendentes: 1', pdf_content)

    def test_template_strings(self):
        # Check that template strings are present
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.general_report_url)
        pdf_content = self.extract_text_from_pdf(response.content)

        self.assertIn('Relatório Geral da Academia', pdf_content)
        self.assertIn('Resumo de Alunos', pdf_content)
        self.assertIn('Resumo da Receita', pdf_content)
        self.assertIn('Detalhes dos Pagamentos', pdf_content)

    def test_empty_payments(self):
        # Test behavior when there are no payments
        Payment.objects.all().delete()
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.general_report_url)
        pdf_content = self.extract_text_from_pdf(response.content)

        self.assertIn('R$0,00', pdf_content)  # Total revenue should be zero

    def test_multiple_members(self):
        # Test with multiple active and inactive members
        Member.objects.create(full_name='Another Active Member', email='active2@example.com', is_active=True)
        Member.objects.create(full_name='Another Inactive Member', email='inactive2@example.com', is_active=False)
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.general_report_url)
        pdf_content = self.extract_text_from_pdf(response.content)

        self.assertIn('Alunos Ativos: 2', pdf_content)
        self.assertIn('Alunos Pendentes: 2', pdf_content)

    def test_large_revenue(self):
        # Test behavior with large payments
        Payment.objects.create(member=self.member_active, amount=900.99, payment_date=localdate())
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.general_report_url)
        pdf_content = self.extract_text_from_pdf(response.content)

        self.assertIn('R$1050,99', pdf_content)  # Total revenue

    def test_invalid_methods(self):
        # Test unsupported HTTP methods
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.post(self.general_report_url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        response = self.client.put(self.general_report_url)
        self.assertEqual(response.status_code, 405)
        response = self.client.delete(self.general_report_url)
        self.assertEqual(response.status_code, 405)
        
    @patch('admin_panel.views.pisa.CreatePDF')
    def test_error_in_pdf_generation(self, mock_create_pdf):
        mock_create_pdf.return_value.err = True
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.general_report_url)
        
        messages = list(response.wsgi_request._messages)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Erro ao gerar o PDF.')
        
        
class GeneratePDFReportOfCurrentDayTestCase(TestBaseReportViews):

    def test_requires_authentication(self):
        # Ensure only authenticated users can access the view
        response = self.client.get(self.current_day_report_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertIn('/users/login/', response.url)

    def test_authenticated_access(self):
        # Log in and test access
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.current_day_report_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename=gym_current_day_report_'))

    def test_template_rendering(self):
        # Test if the template is rendered correctly and includes all necessary content
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.current_day_report_url)

        pdf_content = self.extract_text_from_pdf(response.content)

        # Check if the template variables are rendered in the PDF content
        self.assertIn('Relatório Diário da Academia', pdf_content)
        self.assertIn('Alunos Ativos: 1', pdf_content)
        self.assertIn('Alunos Inativos: 1', pdf_content)
        self.assertIn('Receita Total: R$150,00', pdf_content)

    def test_context_data(self):
        # Check if context data is correctly passed to the template
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.current_day_report_url)

        self.assertEqual(response.status_code, 200)
        pdf_content = self.extract_text_from_pdf(response.content)

        # Check that the active and inactive members count is correct
        self.assertIn('Alunos Ativos: 1', pdf_content)
        self.assertIn('Alunos Inativos: 1', pdf_content)

        # Check that total revenue is calculated correctly
        self.assertIn('Receita Total: R$150,00', pdf_content)

    def test_no_report_found(self):
        # Simulate no report being found for the current date
        DailyReport.objects.all().delete()  # Remove any existing reports
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.current_day_report_url)
        
        self.assertEqual(response.status_code, 200)
        pdf_content = self.extract_text_from_pdf(response.content)

        # Verify that the default report is generated (after calling create_report)
        self.assertIn('Alunos Ativos: 1', pdf_content)
        self.assertIn('Alunos Inativos: 1', pdf_content)
        self.assertIn('Receita Total: R$150,00', pdf_content)

    def test_no_payments_today(self):
        # Simulate no payments today
        Payment.objects.all().delete()  # Remove all payments
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.current_day_report_url)
        
        self.assertEqual(response.status_code, 200)
        pdf_content = self.extract_text_from_pdf(response.content)

        # Verify that the 'No Payments Registered Today' message appears
        self.assertIn('Nenhum Pagamento Registrado Hoje', pdf_content)

    def test_multiple_members(self):
        # Test with multiple active and inactive members
        Member.objects.create(full_name='Another Active Member', email='active2@example.com', is_active=True)
        Member.objects.create(full_name='Another Inactive Member', email='inactive2@example.com', is_active=False)
        
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.current_day_report_url)
        
        pdf_content = self.extract_text_from_pdf(response.content)

        self.assertIn('Alunos Ativos: 2', pdf_content)
        self.assertIn('Alunos Inativos: 2', pdf_content)

    @patch('admin_panel.views.pisa.CreatePDF')
    def test_error_in_pdf_generation(self, mock_create_pdf):
        # Simulate an error during PDF generation
        mock_create_pdf.return_value.err = True
        
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.current_day_report_url)

        messages = list(response.wsgi_request._messages)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Erro ao gerar o PDF.')

    def test_invalid_methods(self):
        # Test unsupported HTTP methods
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.post(self.current_day_report_url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        response = self.client.put(self.current_day_report_url)
        self.assertEqual(response.status_code, 405)
        response = self.client.delete(self.current_day_report_url)
        self.assertEqual(response.status_code, 405)