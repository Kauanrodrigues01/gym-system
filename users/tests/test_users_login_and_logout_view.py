from django.urls import reverse
from django.contrib.messages import get_messages
from users.tests.base.test_base import TestBase

class LoginViewTests(TestBase):
    
    def test_login_view_get(self):
        """Testa se o formulário de login é exibido corretamente."""
        response = self.client.get(self.login_view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, '<input type="text" name="cpf"')
        self.assertContains(response, '<input type="password" name="password"')
    
    def test_login_view_redirect_if_authenticated(self):
        """Testa se o login redireciona para a página de administração se o usuário já estiver autenticado."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.login_view_url)
        self.assertRedirects(response, reverse('admin_panel:home'))
        
    def test_login_submit_without_post_data(self):
        """Testa se a view redireciona corretamente quando nenhuma requisição POST é enviada."""
        response = self.client.get(self.login_submit_url)
        self.assertRedirects(response, self.login_view_url)

    def test_login_submit_authenticated_user(self):
        """Testa se um usuário autenticado é redirecionado corretamente."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.post(self.login_submit_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.admin_home_url)

    def test_login_submit_valid_data(self):
        """Testa se o login é bem-sucedido com CPF e senha válidos."""
        response = self.client.post(self.login_submit_url, {
            'cpf': self.user.cpf,
            'password': self.password
        })
        self.assertRedirects(response, reverse('admin_panel:home'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Login bem-sucedido!')

    def test_login_submit_invalid_cpf(self):
        """Testa se o login falha com CPF inválido."""
        response = self.client.post(self.login_submit_url, {
            'cpf': '00000000000',  # CPF inválido
            'password': self.password
        })
        self.assertRedirects(response, self.login_view_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'CPF ou senha inválidos.')

    def test_login_submit_invalid_password(self):
        """Testa se o login falha com senha inválida."""
        response = self.client.post(self.login_submit_url, {
            'cpf': self.user.cpf,
            'password': 'wrongpassword'  # Senha errada
        })
        self.assertRedirects(response, self.login_view_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'CPF ou senha inválidos.')
        
    def test_login_submit_invalid_form(self):
        """Testa se o login falha quando o formulário é inválido."""
        response = self.client.post(self.login_submit_url, {
            'cpf': 'invalid_cpf',  # CPF inválido
            'password': ''  # Senha vazia
        })
        self.assertRedirects(response, self.login_view_url)  # Espera redirecionamento para a página de login
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'CPF ou senha inválidos.')


    def test_login_form_data_stored_in_session(self):
        """Testa se os dados do formulário de login são armazenados na sessão."""
        response = self.client.post(self.login_submit_url, {
            'cpf': self.user.cpf,
            'password': 'ahasdask'
        })
        self.assertRedirects(response, self.login_view_url)
        # Verifica se os dados do formulário são armazenados na sessão
        self.assertIn('login_form_data', self.client.session)

    def test_login_with_authenticated_user(self):
        """Testa se um usuário autenticado não pode acessar o formulário de login."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.login_view_url)
        self.assertRedirects(response, reverse('admin_panel:home'))


class LogoutViewTests(TestBase):

    def test_logout_view(self):
        """Testa se o logout funciona corretamente."""
        self.client.login(cpf=self.user.cpf, password=self.password)
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_view_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Logout bem-sucedido!')

    def test_logout_view_redirect_if_not_authenticated(self):
        """Testa se o logout redireciona corretamente se o usuário não estiver autenticado."""
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_view_url)
