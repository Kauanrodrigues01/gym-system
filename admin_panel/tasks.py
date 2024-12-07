from .models import DailyReport
from celery import shared_task

@shared_task
def save_daily_report():
    DailyReport.create_report()