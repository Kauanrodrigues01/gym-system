from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes


class PasswordResetViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Configura o usuário e URLs para os testes de redefinição de senha"""
        cls.password = 'password123'
        cls.user = get_user_model().objects.create_user(
            cpf='12345678901',
            email='user@example.com',
            password=cls.password
        )
        # URLs de todas as views necessárias
        cls.password_reset_url = reverse('users:password_reset')
        cls.password_reset_send_url = reverse('users:password_reset_send')
        cls.password_reset_confirm_url = reverse('users:password_reset_confirm', kwargs={'uidb64': urlsafe_base64_encode(smart_bytes(cls.user.id)), 'token': PasswordResetTokenGenerator().make_token(cls.user)})
        cls.password_reset_complete_url = reverse('users:password_reset_complete')
        cls.login_url = reverse('users:login_view')
        cls.admin_home_url = reverse('admin_panel:home')

    def test_password_reset_view_get(self):
        """Testa se o formulário de redefinição de senha é exibido corretamente"""
        response = self.client.get(self.password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Redefinir Senha')
        self.assertContains(response, '<input type="email" name="email"')
        
    def test_password_reset_view_redirect_if_authenticated(self):
        """Testa se o login redireciona para a página de administração se o usuário já estiver autenticado."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.password_reset_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.admin_home_url)
        
    def test_password_reset_send_without_post_data(self):
        response = self.client.get(self.password_reset_send_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.password_reset_url)
            
    def test_password_reset_send_valid_email(self):
        """Testa se o envio de um e-mail válido para redefinir a senha envia o link"""
        response = self.client.post(self.password_reset_send_url, {
            'email': 'user@example.com'
        })
        self.assertRedirects(response, self.login_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Se o e-mail existir, um link para redefinir sua senha foi enviado.")
    
    def test_password_reset_send_invalid_email(self):
        """Testa se o envio de um e-mail inválido gera um erro"""
        response = self.client.post(self.password_reset_send_url, {
            'email': 'nonexistent@example.com'
        })
        self.assertRedirects(response, self.password_reset_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Por favor, corrija os erros abaixo.')
    
    def test_password_reset_send_invalid_email_format(self):
        """Testa se o formato do e-mail inválido gera um erro"""
        response = self.client.post(self.password_reset_send_url, {
            'email': 'invalidemail'
        })
        self.assertRedirects(response, self.password_reset_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Por favor, corrija os erros abaixo.')

    
    def test_password_reset_confirm_view_get(self):
        """Testa se o formulário de redefinição de senha com a nova senha é exibido corretamente"""
        response = self.client.get(self.password_reset_confirm_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nova Senha')
        self.assertContains(response, '<input type="password" name="password"')
        
    def test_password_reset_confirm_authenticated_user(self):
        """Testa se um usuário autenticado é redirecionado para a página de administração ao tentar redefinir a senha"""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.password_reset_confirm_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.admin_home_url)
    
    def test_password_reset_confirm_invalid_token(self):
        """Testa se o link de redefinição de senha com token inválido gera erro"""
        invalid_token = 'invalidtoken'
        url = reverse('users:password_reset_confirm', kwargs={'uidb64': urlsafe_base64_encode(smart_bytes(self.user.id)), 'token': invalid_token})
        response = self.client.get(url)
        self.assertRedirects(response, self.password_reset_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Link expirado ou inválido. Faça a solicitação novamente.')

    def test_password_reset_complete_redirect_if_not_post(self):
        """Testa se redireciona para password reset se a requisição não for POST"""
        response = self.client.get(self.password_reset_complete_url)
        self.assertRedirects(response, self.password_reset_url)

    def test_password_reset_complete_with_missing_session_data(self):
        response = self.client.get(self.password_reset_confirm_url)

        # Limpa o cookie de sessão diretamente
        self.client.cookies['sessionid'] = ''  # Limpa o cookie de sessão

        response = self.client.post(self.password_reset_complete_url, {
            'password': 'NewPassword123',
            'password_confirm': 'NewPassword123'
        })

        self.assertRedirects(response, self.password_reset_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'O link de redefinição expirou ou não foi encontrado.')

    def test_password_reset_with_invalid_uidb64_session_data(self):
        response = self.client.get(self.password_reset_confirm_url)
        
        request = response.wsgi_request
        request.session['reset_password_data'] = {
            'uidb64': urlsafe_base64_encode(smart_bytes('invalid-uidb64')),
            'token': PasswordResetTokenGenerator().make_token(self.user)
        }
        request.session.save() 

        response = self.client.post(self.password_reset_complete_url, {
            'password': 'NewPassword123',
            'password_confirm': 'NewPassword123',
        })

        self.assertRedirects(response, self.password_reset_url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Link inválido.')

    def test_password_reset_with_invalid_token_session_data(self):
        response = self.client.get(self.password_reset_confirm_url)
        
        request = response.wsgi_request
        request.session['reset_password_data'] = {
            'uidb64': urlsafe_base64_encode(smart_bytes(self.user.id)),
            'token': 'invalid_token'
        }
        request.session.save() 

        response = self.client.post(self.password_reset_complete_url, {
            'password': 'NewPassword123',
            'password_confirm': 'NewPassword123',
        })

        self.assertRedirects(response, self.password_reset_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Link expirado ou inválido. Faça a solicitação novamente.')
    
    def test_password_reset_complete_valid(self):
        """Testa se a redefinição de senha é realizada com sucesso"""
        response = self.client.get(self.password_reset_confirm_url)
        response = self.client.post(self.password_reset_complete_url, {
            'password': 'NewPassword123',
            'password_confirm': 'NewPassword123'
        })
        self.assertRedirects(response, self.login_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Senha redefinida com sucesso!')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123'))

    def test_password_reset_complete_invalid_passwords(self):
        """Testa se a redefinição de senha falha se as senhas não coincidirem"""
        response = self.client.get(self.password_reset_confirm_url)
        response = self.client.post(self.password_reset_complete_url, {
            'password': 'NewPassword123',
            'password_confirm': 'DifferentPassword123'
        })
        self.assertEqual(response.status_code, 302)  # Redireciona de volta ao formulário
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Por favor, corrija os erros abaixo.')

    def test_password_reset_complete_invalid_password_format(self):
        """Testa se a redefinição de senha falha se a nova senha não atender aos requisitos de segurança"""
        response = self.client.get(self.password_reset_confirm_url)
        response = self.client.post(self.password_reset_complete_url, {
            'password': 'short',
            'password_confirm': 'short'
        })
        self.assertEqual(response.status_code, 302)  # Redireciona de volta ao formulário
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Por favor, corrija os erros abaixo.')
        
    def test_password_reset_complete_invalid_link(self):
        """Testa se um link inválido (ID ou token errado) leva à página de erro"""
        invalid_token = 'invalidtoken'
        invalid_uidb64 = 'invaliduidb64'
        url = reverse('users:password_reset_confirm', kwargs={'uidb64': invalid_uidb64, 'token': invalid_token})
        response = self.client.get(url)
        self.assertRedirects(response, self.password_reset_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Link inválido.')
