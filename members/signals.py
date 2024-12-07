from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Member, Payment
from admin_panel.models import ActivityLog

@receiver(post_save, sender=Member)
def log_member_activity(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            member=instance,
            event_type='created',
            description=f"Aluno {instance.full_name} foi cadastrado."
        )
    else:
        ActivityLog.objects.create(
            member=instance,
            event_type='updated',
            description=f"Aluno {instance.full_name} foi atualizado."
        )


@receiver(post_delete, sender=Member)
def log_member_deleted_activity(sender, instance, **kwargs):
    ActivityLog.objects.create(
        event_type='deleted',
        description=f"Aluno {instance.full_name} foi excluído."
    )


@receiver(post_save, sender=Payment)
def log_payment_activity(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            member=instance.member,
            event_type='payment',
            description=f"{f'Aluno {instance.member.full_name}' if instance.member else 'Pagamento sem aluno associado |'} realizou um pagamento de R$ {instance.amount}."
        )
