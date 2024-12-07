from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
from utils.utils import is_valid_cpf

class UserManager(BaseUserManager):
    def create_user(self, cpf=None, email=None, full_name=None, password=None, **extra_fields):
        if not cpf:
            raise ValueError("O CPF é obrigatório.")
        if not email:
            raise ValueError("O email é obrigatório.")
        
        email = self.normalize_email(email)
        user = self.model(cpf=cpf, email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(cpf, email, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    cpf = models.CharField("CPF", max_length=11, unique=True)
    email = models.EmailField("Email", unique=True)
    full_name = models.CharField("Nome completo", max_length=255, blank=True, null=True)
    is_active = models.BooleanField("Ativo", default=True)
    is_staff = models.BooleanField("Membro da equipe", default=False)

    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return f"{self.full_name or 'User'} ({self.cpf})"
    
    def clean(self):
        if not is_valid_cpf(self.cpf):
            raise ValidationError({'cpf': 'CPF inválido.'})
            
        return super().clean()
