from django.db import models
from datetime import timedelta
from django.utils.timezone import localdate
from django.db.models import Sum, Min, Max, Count
from django.core.exceptions import ValidationError
from datetime import datetime
from django.core.validators import MinLengthValidator
from utils.ultramsg import UltraMsgAPI

class Member(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=50, validators=[MinLengthValidator(3)])
    phone = models.CharField(max_length=15)
    start_date = models.DateField(default=localdate)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.full_name}'

    @property
    def last_payment_date(self):
        """Retorna a última data de pagamento do membro ou None se não houver pagamentos."""
        
        last_payment = self.payments.aggregate(last_payment=Max('payment_date'))['last_payment']
        
        return last_payment

    def update_activity_status(self):
        """Atualiza o status de atividade do membro com base na última data de pagamento."""
        now = localdate()

        if self.last_payment_date and self.last_payment_date < now - timedelta(days=30):
            self.is_active = False
            BillingMessage.objects.get_or_create(
                member=self,
                is_sent=False,
            )
        else:
            self.is_active = True
            
        self.save()
    

class Payment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, related_name='payments')
    payment_date = models.DateField(default=localdate)
    amount = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    
    def __str__(self):
        if self.member:
            return f'{self.member.full_name} | {self.payment_date} | R$ {self.amount}'
        else:
            return f'Pagamento sem aluno associado | {self.payment_date} | R$ {self.amount}'
    
    @classmethod
    def get_current_month_profit(cls):
        """Calcula o total de pagamento rebido no mês atual"""
        current_month = localdate().month
        current_year = localdate().year
        
        payments = Payment.objects.filter(
            payment_date__month=current_month,
            payment_date__year=current_year
        )
        
        # Nessa linha agrega um campo chamado total_in_the_month, mas esse campo não existe no modelo Payment, então tem que ser chamado como se fosse uma chave do dicionário
        payments = payments.aggregate(total_in_the_month=Sum('amount'))
        
        return payments['total_in_the_month'] or 0.00
    
    @classmethod
    def get_monthly_profit(cls, month=1):
        """Calcula o total de pagamento recebido em um mês"""
        if not (1 <= month <= 12):
            raise ValidationError("Month must be between 1 and 12.")
        
        # Cria um objeto datetime com o primeiro dia do mês
        current_year = localdate().year
        month_start_date = datetime(current_year, month, 1)
        
        # Usa o mês obtido para filtrar os pagamentos
        payments = Payment.objects.filter(
            payment_date__year=current_year,
            payment_date__month=month_start_date.month  # Usando o mês como atributo
        )
        
        payments = payments.aggregate(total_in_the_month=Sum('amount'))
        
        return payments['total_in_the_month'] or 0.00
    
    @classmethod
    def get_current_year_profit(cls):
        current_year = localdate().year
        
        payments = Payment.objects.filter(
            payment_date__year=current_year
        )
        
        payments = payments.aggregate(total_in_the_year=Sum('amount'))
        
        return payments['total_in_the_year'] or 0.00
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.member:
            self.member.update_activity_status()
            

class BillingMessage(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='billing_messages')
    created_at = models.DateField(default=localdate)  # Data local em que a mensagem foi salva
    is_sent = models.BooleanField(default=False)  # Flag para saber se já foi enviada

    def __str__(self):
        return f"BillingMessage for {self.member.full_name} - Sent: {self.is_sent}"
    
    def send_message(self):
        ultramsg = UltraMsgAPI()
        
        message = f"Olá, {self.member.full_name}! Seu pagamento está atrasado. Por favor, regularize sua situação."
        response = ultramsg.send_message(to=f'55{self.member.phone}', message=message)
        
        if response.status_code == 200 and 'true' in response.text:
            self.is_sent = True
            self.save()
        else:
            print(f"Error sending message to {self.member.full_name}: {response.text}")