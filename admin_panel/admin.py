from django.contrib import admin
from .models import ActivityLog, DailyReport
# Register your models here.

admin.site.register(DailyReport)
admin.site.register(ActivityLog)
