from django import forms
from .models import Member, Payment
from .models import Member
from django.utils.timezone import localdate
import re
from django.core.exceptions import ValidationError

class MemberPaymentForm(forms.Form):
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(
            attrs={
               'id': 'student-email',
                'class': 'form-control',
                'required': True ,
                'placeholder': 'Digite o email do aluno'
            }
        )
    )
    full_name = forms.CharField(
        max_length=50,
        min_length=3,
        label='Nome Completo',
        widget=forms.TextInput(
            attrs={
                'id': 'student-name',
                'class': 'form-control',
                'required': True,
                'placeholder': 'Nome do aluno'
            }
        ),
        error_messages = {
            'required': 'O nome completo é obrigatório.',
            'min_length': 'O nome completo deve ter pelo menos 3 caracteres.',
            'max_length': 'O nome completo deve ter menos de 50 caracteres.',
        }
    )
    phone = forms.CharField(
        max_length=15,
        label='Telefone',
        widget=forms.TextInput(attrs={
            'id': 'student-phone',
            'class': 'form-control',
            'placeholder': 'Digite apenas números',
            'required': True
        })
    )
    is_active = forms.ChoiceField(
        label='Status',
        required=True,
        choices=[(True, 'Ativo'), (False, 'Pendente')],
        widget=forms.Select(attrs={
            'id': 'student-status',
            'class': 'form-select',
        }),
    )
    
    payment_date = forms.DateField(
        label='Data de Pagamento',
        widget=forms.DateInput(attrs={
            'id': 'payment-date',
            'class': 'form-control',
            'type': 'date',
            'required': True
        })
    )
    amount = forms.DecimalField(
        max_digits=5, decimal_places=2,
        label='Valor',
        initial=100.00,
        widget=forms.NumberInput(attrs={
            'id': 'amount',
            'class': 'form-control',
            'required': True,
            'step': '0.5',
            'min': '0.00'   
        })
    )
    

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Member.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone').replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        if not re.match(r'^\d{10,15}$', phone):
            raise forms.ValidationError('O telefone deve conter apenas números e ter entre 10 e 15 dígitos.')
        return phone
    
    def clean_payment_date(self):
        payment_date = self.cleaned_data.get('payment_date')

        if payment_date > localdate():
            raise forms.ValidationError('A data de pagamento não pode ser no futuro.')

        return payment_date
    
    def save(self):
        # Criar um novo membro
        member = Member.objects.create(
            email=self.cleaned_data['email'],
            full_name=self.cleaned_data['full_name'],
            phone=self.cleaned_data['phone'],
            is_active=self.cleaned_data.get('is_active', False)
        )

        # Criar o pagamento associado ao membro
        Payment.objects.create(
            member=member,
            payment_date=self.cleaned_data['payment_date'],
            amount=self.cleaned_data['amount']
        )

        return member

class MemberEditForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['full_name', 'email', 'phone', 'is_active']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'id': 'student-name',
                'class': 'form-control',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'id': 'student-email',
                'class': 'form-control',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'id': 'student-phone',
                'class': 'form-control',
                'placeholder': 'Digite apenas números',
                'required': True
            }),
            'is_active': forms.Select(attrs={
                'id': 'student-status',
                'class': 'form-control',
            }, choices=[(True, 'Ativo'), (False, 'Pendente')]),
        }
        labels = {
            'full_name': 'Nome Completo',
            'email': 'E-mail',
            'phone': 'Telefone',
            'is_active': 'Status'
        }
        error_messages = {
            'full_name': {
                'required': 'O nome completo é obrigatório.',
                'min_length': 'O nome completo deve ter pelo menos 3 caracteres.',
                'max_length': 'O nome completo deve ter menos de 50 caracteres.'
            }
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if Member.objects.exclude(id=self.instance.id).filter(email=email).exists():
            raise forms.ValidationError('Já existe um aluno com este e-mail.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone').replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        if not re.match(r'^\d{10,15}$', phone):
            raise forms.ValidationError('O telefone deve conter apenas números e ter entre 10 e 15 dígitos.')
        return phone

    def clean_is_active(self):
        is_active = self.cleaned_data['is_active']
        return is_active

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_date', 'amount']
        
        widgets = {
            'payment_date': forms.DateInput(
                attrs={
                    'id': 'payment-date',
                    'class': 'form-control',
                    'type': 'date',
                    'required': True
                }
            ),
            'amount': forms.NumberInput(
                attrs={
                    'id': 'amount',
                    'class': 'form-control',
                    'required': True,
                    'step': '0.5',
                    'min': '0.00'
                }
            )
        }
        labels = {
            'payment_date': 'Data de Pagamento',
            'amount': 'Valor'
        }
        
    def clean_payment_date(self):
        payment_date = self.cleaned_data.get('payment_date')

        if payment_date > localdate():
            raise forms.ValidationError('A data de pagamento não pode ser no futuro.')

        return payment_date
        
    def save(self, commit=True, member=None):
        if not member:
            raise ValidationError('É necessário fornecer um membro ao salvar o pagamento.')
        
        payment = super().save(commit=False)
        payment.member = member
        
        if commit:
            payment.save()
            
        
        return payment