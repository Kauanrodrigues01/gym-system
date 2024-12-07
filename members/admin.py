from django.contrib import admin
from .models import Member, Payment, BillingMessage
# Register your models here.

admin.site.register(Payment)
admin.site.register(Member)
admin.site.register(BillingMessage)