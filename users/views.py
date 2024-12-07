from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm, PasswordResetRequestForm, PasswordResetForm
from users.models import User
from django.urls import reverse
from django.shortcuts import get_object_or_404

from django.utils.encoding import smart_bytes, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from utils.utils import send_email


    
def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_panel:home')
    
    login_form_data = request.session.get('login_form_data', {})
    form = LoginForm(login_form_data)

    context = {
        'form': form
    }
    return render(request, 'users/pages/login.html', context)

def login_submit(request):
    if request.user.is_authenticated:
        return redirect('admin_panel:home')
    
    if not request.POST:
        return redirect('users:login_view')


    POST = request.POST
    request.session['login_form_data'] = POST 

    form = LoginForm(POST)

    if form.is_valid():
        cpf = form.cleaned_data['cpf']
        password = form.cleaned_data['password']

        user = authenticate(request, cpf=cpf, password=password)

        if user is not None:
            login(request, user) 
            messages.success(request, "Login bem-sucedido!")

            return redirect('admin_panel:home') 

        else:
            messages.error(request, "CPF ou senha inválidos.")
            return redirect('users:login_view')
    else:
        messages.error(request, "CPF ou senha inválidos.")
        return redirect('users:login_view')

def logout_view(request):
    logout(request)
    messages.success(request, "Logout bem-sucedido!")
    return redirect('users:login_view')



def password_reset(request):
    """Carrega o formulário de redefinição de senha, com o campo de e-mail."""
    if request.user.is_authenticated:
        return redirect('admin_panel:home')
    
    form_data = request.session.get('reset_password_form_data', {})
    form = PasswordResetRequestForm(form_data)

    context = {
        'form': form
    }

    return render(request, 'users/pages/password_reset_email_form.html', context)

def password_reset_send(request):
    """ Recebe o formulario de redefinição com o email para redefinição de senha e envia um e-mail com o link para redefinir a senha."""
    if request.method != 'POST':
        return redirect('users:password_reset')
    
    form = PasswordResetRequestForm(request.POST)

    # Salva os dados do formulário na sessão
    request.session['reset_password_form_data'] = request.POST

    if form.is_valid():
        email = form.cleaned_data['email']
        user = get_object_or_404(User, email=email)

        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        current_site = get_current_site(request).domain
        relative_link = reverse('users:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        absurl = f'http://{current_site}{relative_link}'
        
        full_name = user.full_name or ' '
        first_name = full_name.split(' ')[0]
        email_body = f'Olá, {first_name}.\n Redefina sua senha usando o link abaixo: \n {absurl}'
        
        send_email(
            subject='Reset da senha',
            message=email_body,
            to_email=user.email
        )
        messages.success(request, "Se o e-mail existir, um link para redefinir sua senha foi enviado.")
        return redirect('users:login_view') 
    else:
        messages.error(request, "Por favor, corrija os erros abaixo.")

    return redirect('users:password_reset') 
 
 
 
def password_reset_confirm(request, uidb64, token):
    """Carrega o formulário de redefinição de senha, com os campos de nova senha e confirmação de senha."""
    if request.user.is_authenticated:
        return redirect('admin_panel:home')
    
    request.session['reset_password_data'] = {
        'uidb64': uidb64,
        'token': token
    }
    
    try:
        user_id = smart_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=user_id)
    except (User.DoesNotExist, ValueError, TypeError):
        del request.session['reset_password_data']
        messages.error(request, 'Link inválido.')
        return redirect('users:password_reset')
    
    if not PasswordResetTokenGenerator().check_token(user, token):
        del request.session['reset_password_data']
        messages.error(request, 'Link expirado ou inválido. Faça a solicitação novamente.')
        return redirect('users:password_reset')
    
    form_password_reset_data = request.session.get('form_password_reset_data')
    form = PasswordResetForm(form_password_reset_data)
    
    context = {
        'form': form
    }
    
    return render(request, 'users/pages/password_reset_confirm_form.html', context)

def password_reset_complete(request):
    """Recebe o formulário de redefinição de senha e redefini a senha do usuário."""
    if request.method != 'POST':
        return redirect('users:password_reset') 
    
    reset_password_data = request.session.get('reset_password_data')
    
    if not reset_password_data:
        messages.error(request, 'O link de redefinição expirou ou não foi encontrado.')
        return redirect('users:password_reset')
    
    uidb64 = reset_password_data['uidb64']
    token = reset_password_data['token']
    
    try:
        user_id = smart_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=user_id)
    except (User.DoesNotExist, ValueError, TypeError):
        del request.session['reset_password_data']
        messages.error(request, 'Link inválido.')
        return redirect('users:password_reset')
    
    request.session['form_password_reset_data'] = request.POST
    
    if PasswordResetTokenGenerator().check_token(user, token):
        form = PasswordResetForm(request.POST)
        
        if form.is_valid():
            password = form.cleaned_data['password']
            
            user.set_password(password)
            user.save()
            
            del request.session['reset_password_data']
            messages.success(request, 'Senha redefinida com sucesso!')
            return redirect('users:login_view')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
            url = reverse('users:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
            return redirect(url)
    else:
        del request.session['reset_password_data']
        messages.error(request, 'Link expirado ou inválido. Faça a solicitação novamente.')
        return redirect('users:password_reset')
        
