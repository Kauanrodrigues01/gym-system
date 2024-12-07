from celery import shared_task
from .models import Member, BillingMessage

@shared_task
def update_members_activity_status():
    """Verifica se o pagamento do membro foi feito há mais de 1 mês e atualiza o status."""
    members = Member.objects.filter(is_active=True)

    for member in members:
        member.update_activity_status()
        
@shared_task
def send_billing_messages():
    """Envia mensagens de cobrança para os membros inativos."""
    pendent_messages = BillingMessage.objects.filter(is_sent=False, member__is_active=False)[:100]
    
    for message in pendent_messages:
        message.send_message()