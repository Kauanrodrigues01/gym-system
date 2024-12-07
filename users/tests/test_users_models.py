from django.core.exceptions import ValidationError
from users.models import User
from users.tests.base.test_base import TestBase

class UserModelTests(TestBase):

    def test_create_user_with_valid_data(self):
        """Testa a criação de um usuário com dados válidos."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.cpf, self.valid_cpf)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.full_name, self.user_data['full_name'])
        self.assertTrue(user.check_password(self.user_data['password']))
        
    def test_create_user_with_valid_cpf_does_not_raise_error(self):
        """Testa se a criação de um usuário com CPF válido não gera erro de validação."""
        self.user_data['cpf'] = self.valid_cpf
        user = User(**self.user_data)
        
        try:
            user.clean()
        except ValidationError as e:
            self.fail(f"O método clean() gerou um erro de validação: {e}")

    def test_create_user_without_cpf_raises_error(self):
        """Testa se a criação de um usuário sem CPF gera um erro."""
        self.user_data.pop('cpf')  # Remove o CPF
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(**self.user_data)  # Chama create_user com cpf ausente
        self.assertEqual(str(context.exception), 'O CPF é obrigatório.')  # Mensagem de erro correta

    def test_create_user_without_email_raises_error(self):
        """Testa se a criação de um usuário sem email gera um erro."""
        self.user_data.pop('email')  # Remove o email
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(**self.user_data)  # Chama create_user com email ausente
        self.assertEqual(str(context.exception), 'O email é obrigatório.')

    def test_create_user_with_invalid_cpf_raises_validation_error(self):
        """Testa se a criação de um usuário com CPF inválido gera erro de validação."""
        self.user_data['cpf'] = self.invalid_cpf
        user = User(**self.user_data)
        with self.assertRaises(ValidationError) as context:
            user.clean()
        self.assertIn('CPF inválido.', context.exception.message_dict['cpf'])

    def test_create_superuser(self):
        """Testa a criação de um superusuário."""
        superuser = User.objects.create_superuser(
            cpf=self.valid_cpf, email='admin@example.com', password='adminpass'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_superuser_default_values(self):
        """Testa os valores padrão do superusuário."""
        superuser = User.objects.create_superuser(
            cpf=self.valid_cpf, email='admin@example.com', password='adminpass'
        )
        self.assertTrue(superuser.is_active)

    def test_user_string_representation(self):
        """Testa a representação em string do usuário."""
        user = User.objects.create_user(**self.user_data)
        expected_representation = f'{self.user_data["full_name"]} ({self.user_data["cpf"]})'
        self.assertEqual(str(user), expected_representation)

    def test_user_string_representation_without_full_name(self):
        """Testa a representação em string do usuário sem nome completo."""
        self.user_data['full_name'] = None
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), f'User ({self.user_data["cpf"]})')

    def test_user_default_values(self):
        """Testa os valores padrão do modelo de usuário."""
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
