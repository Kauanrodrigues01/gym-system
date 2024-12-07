from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Configura o ambiente de Django para usar as configurações do arquivo settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Criação da instância Celery
app = Celery('project')

# Usando a configuração do Django para Celery (vai buscar as configurações em settings.py)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carregar todas as tasks registrados em todos os arquivos tasks.py dos apps
app.autodiscover_tasks()
