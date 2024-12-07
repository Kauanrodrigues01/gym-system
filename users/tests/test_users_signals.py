from django.test import TestCase
from django.apps import apps
from django.db.models.signals import post_migrate
from decouple import config
from users.models import User
from users.signals import create_superuser

class CreateSuperuserSignalTest(TestCase):

    def test_create_superuser_signal(self):
        """
        Testa se o superusuário é criado corretamente pelo signal `create_superuser`
        após o comando de migração.
        """
        
        cpf = config('DJANGO_SUPERUSER_CPF', default='12345678901')
        User.objects.all().delete()

        self.assertFalse(User.objects.filter(cpf=cpf).exists())

        # Recupera o app_config do app onde o modelo está
        app_config = apps.get_app_config('users')

        post_migrate.send(sender=self.__class__, app_config=app_config, verbosity=1)

        self.assertTrue(User.objects.filter(cpf=cpf).exists())