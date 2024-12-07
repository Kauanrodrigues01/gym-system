# scripts/populate_members.py

from django.utils import timezone
from datetime import timedelta
from members.models import Member, Payment

def generate_fake_member_name(index):
    return f'Aluno {index}'

def run():
    # Adicionando 20 membros
    for i in range(21, 100):
        email = f'Aluno{i}@exemplo.com'
        
        # Tenta obter ou criar o membro com o email único
        member, created = Member.objects.get_or_create(
            email=email,
            defaults={
                'full_name': generate_fake_member_name(i),
                'phone': f'99999{i:04d}',
                'start_date': timezone.now() - timedelta(days=i*30),
                'is_active': True if i % 2 == 0 else False
            }
        )

        # Verifica se o membro foi criado e adiciona um pagamento
        if created:
            Payment.objects.create(
                member=member,
                payment_date=timezone.now() - timedelta(days=i*10),
                amount=100.00 + (i * 5)
            )

    print("20 membros e seus pagamentos foram adicionados com sucesso.")
