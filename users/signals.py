from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import User
from decouple import config

@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    cpf = config('DJANGO_SUPERUSER_CPF', default='12345678901')  
    email = config('DJANGO_SUPERUSER_EMAIL', default='admin@example.com')
    password = config('DJANGO_SUPERUSER_PASSWORD', default='admin123')

    if not User.objects.filter(cpf=cpf).exists() and not User.objects.filter(email=email):
        User.objects.create_superuser(cpf=cpf, email=email, password=password)
        print(f"Superuser with CPF '{cpf}' created.")
