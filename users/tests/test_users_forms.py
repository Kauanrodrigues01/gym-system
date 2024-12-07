from django.test import TestCase
from users.forms import LoginForm, PasswordResetRequestForm, PasswordResetForm
from django.contrib.auth import get_user_model
from utils.utils import is_valid_cpf
from faker import Faker
from users.tests.base.test_base import TestBase

class LoginFormTests(TestBase):

    def test_valid_form(self):
        """Tests if the form is valid when the CPF and password are correct"""
        faker = Faker('pt_BR')
        form_data = {'cpf': self.valid_cpf, 'password': self.password}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_cpf_format(self):
        """Tests if the CPF is in the correct format"""
        form_data = {'cpf': self.invalid_cpf, 'password': self.password}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['cpf'], ['O CPF fornecido é inválido.'])

    def test_invalid_cpf_digits(self):
        """Tests if the CPF has 11 digits"""
        form_data = {'cpf': '1234567890A', 'password': 'ValidPassword123'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['cpf'], ['O CPF fornecido é inválido.'])

    def test_invalid_cpf_check(self):
        """Tests if the CPF is valid according to the is_valid_cpf function"""
        form_data = {'cpf': '12345678900', 'password': 'ValidPassword123'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['cpf'], ['O CPF fornecido é inválido.'])

    def test_missing_password(self):
        """Tests if the password field is required"""
        form_data = {'cpf': '12345678901'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)


class PasswordResetRequestFormTests(TestBase):

    def test_valid_email(self):
        """Tests if the form accepts a valid email"""
        form_data = {'email': self.email}
        form = PasswordResetRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_invalid_email(self):
        """Tests if the form rejects invalid emails with the correct error message."""
        form_data = {'email': 'invalid-email'}
        form = PasswordResetRequestForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        
        # Verifies if the error message is correct
        self.assertEqual(form.errors['email'], ['O e-mail fornecido não é válido.'])

    def test_email_not_registered(self):
        """Tests if the form rejects an email that is not registered"""
        form_data = {'email': 'nonexistent@example.com'}
        form = PasswordResetRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Este e-mail não está registrado. Verifique novamente.'])

    def test_missing_email(self):
        """Tests if the email field is required"""
        form_data = {}
        form = PasswordResetRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        

class PasswordResetFormTests(TestCase):

    def test_valid_password(self):
        """Tests if the form accepts a valid password"""
        form_data = {'password': 'NewPassword123', 'password_confirm': 'NewPassword123'}
        form = PasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_passwords_do_not_match(self):
        """Tests if the form rejects passwords that do not match"""
        form_data = {'password': 'NewPassword123', 'password_confirm': 'DifferentPassword123'}
        form = PasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password_confirm'], ['As senhas não coincidem.'])

    def test_short_password(self):
        """Tests if the form rejects passwords shorter than 6 characters"""
        form_data = {'password': 'Abcd1', 'password_confirm': 'Abcd1'}
        form = PasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'], ['A senha deve ter pelo menos 6 caracteres.'])

    def test_missing_uppercase(self):
        """Tests if the form rejects passwords without uppercase letters"""
        form_data = {'password': 'password123', 'password_confirm': 'password123'}
        form = PasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'], ['A senha deve conter pelo menos uma letra maiúscula.'])

    def test_missing_number(self):
        """Tests if the form rejects passwords without numbers"""
        form_data = {'password': 'Password!', 'password_confirm': 'Password!'}
        form = PasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'], ['A senha deve conter pelo menos um número.'])

    def test_valid_password_special_characters(self):
        """Tests if the form accepts passwords with special characters"""
        form_data = {'password': '@#$%ValidPassword123!', 'password_confirm': '@#$%ValidPassword123!'}
        form = PasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid())
