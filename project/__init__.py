from __future__ import absolute_import, unicode_literals

# Para garantir que o app do Celery seja carregado quando o Django iniciar
from .celery import app as celery_app

__all__ = ('celery_app',)
