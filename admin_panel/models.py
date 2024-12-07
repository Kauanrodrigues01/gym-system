from django.db import models
from members.models import Member
from django.utils.timezone import localdate
from members.models import Member, Payment
from django.db.models import Sum
from datetime import date as date_instance
from django.utils.timezone import localtime

class ActivityLog(models.Model):
    EVENT_TYPES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('payment', 'Payment'),
        ('pending', 'Pending'),
    ]

    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(default=localtime, editable=False)

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.description}"


class DailyReport(models.Model):
    date = models.DateField(unique=True)
    active_students = models.PositiveIntegerField(default=0)
    pending_students = models.PositiveIntegerField(default=0)
    new_students = models.PositiveIntegerField(default=0)
    daily_profit = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    payments = models.ManyToManyField(Payment)
    

    def __str__(self):
        return f"Daily Report for {self.date}"
    
    class Meta:
        indexes = [
            models.Index(fields=['date']),
        ]
    
    @classmethod
    def create_report(cls, date=None):
        if date and not isinstance(date, date_instance):
            raise ValueError('A data do relatório tem que ser uma instância de date()')
        if date and date > localdate():
            raise ValueError('A data do relatório não pode ser no futuro')
        if date is None:
            date = localdate()
            
        report, created = cls.objects.get_or_create(date=date)
        
        report.active_students = Member.objects.filter(is_active=True).count()
        report.pending_students = Member.objects.filter(is_active=False).count()
        report.new_students = Member.objects.filter(created_at__date=date).count()
        report.daily_profit = Payment.objects.filter(payment_date=date).aggregate(
            daily_profit=Sum('amount')
        )['daily_profit'] or 0.0
        report.payments.set(Payment.objects.filter(payment_date=date))
        
        report.save()
        return report