from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from members.forms import MemberPaymentForm, PaymentForm, MemberEditForm
from .models import ActivityLog
from members.models import Member, Payment
from django.shortcuts import get_object_or_404
from django.utils.timezone import localdate, localtime
from django.db.models import Q, Max
from django.utils.dateparse import parse_date
from utils.utils import make_pagination
from django.contrib import messages

# Create your views here.
@login_required
def home(request):
    current_month = localdate().month
    current_year = localdate().year
    
    
    count_new_members_in_month = Member.objects.filter( created_at__month=current_month, created_at__year=current_year).count()
    profit_total_month = Payment.get_current_month_profit()
    recent_activities = ActivityLog.objects.all().order_by('-id').select_related('member')[:20]
    
    context = {
        'count_members_actives': Member.objects.filter(is_active=True).count(),
        'count_members_inactives': Member.objects.filter(is_active=False).count(),
        'count_new_members_in_month': count_new_members_in_month,
        'profit_total_month': profit_total_month,
        'recent_activities': recent_activities
    }
    return render(request, 'admin_panel/pages/home.html', context)

@login_required
def members(request):
    search_query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    date = request.GET.get('last_payment', '')
    
    # Dealing with filters
    filters = {}
    if search_query:
        filters['full_name__icontains'] = search_query
        
    if status == 'active':
        filters['is_active'] = True
    elif status == 'inactive':
        filters['is_active'] = False
    
    members = Member.objects.filter(**filters).order_by('-id')
    
    if date:
        date = parse_date(date)
        
        members = members.annotate(
            last_payment=Max('payments__payment_date')
        ).filter(last_payment=date)
        

        
    # Dealing with form 
    form_data_add_member = request.session.get('form_data_add_member')
    
    if form_data_add_member:
        form = MemberPaymentForm(form_data_add_member)
        request.session.pop('form_data_add_member', None)
    else:
        form = MemberPaymentForm()
        
        
        
    # Dealing with pagination
    page_obj, pagination_range = make_pagination(request, members, 15, 6)

    context = {
        'form': form,
        'members': page_obj,
        'pagination_range': pagination_range,
        'search_query': search_query
    }
    
    return render(request, 'admin_panel/pages/members.html', context)

@login_required
def edit_member_view(request, id):
    member = get_object_or_404(Member, id=id)

    form_data_edit_member = request.session.pop('form_data_edit_member', None)  # Use pop para remover depois de usar
    
    if form_data_edit_member:
        form = MemberEditForm(form_data_edit_member, instance=member)
    else:
        form = MemberEditForm(instance=member)

    return render(request, 'admin_panel/pages/member_edit.html', {'form': form, 'member': member})

@login_required
def add_payment_view(request, id):
    member = get_object_or_404(Member, id=id)
    form_data_add_payment = request.session.get('form_data_add_payment')
    
    if form_data_add_payment:
        form = PaymentForm(form_data_add_payment)
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'member': member
    }
    
    return render(request, 'admin_panel/pages/add_payment.html', context)


@login_required
def add_member(request):
    if request.method == 'POST':
        form = MemberPaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membro adicionado com sucesso!')
            if 'form_data_add_member' in request.session: # pragma: no cover
                del request.session['form_data_add_member']
            return redirect('admin_panel:members')
        else:
            request.session['form_data_add_member'] = request.POST
            request.session.modified = True
            messages.error(request, 'Erro ao adicionar o membro. Verifique os dados e tente novamente.')
            return redirect('admin_panel:members')
    return redirect('admin_panel:members')

@login_required
def delete_member(request, id):
    member = get_object_or_404(Member, id=id)
    member.delete()
    messages.success(request, 'Membro deletado com sucesso!')
    return redirect('admin_panel:members')

@login_required
def edit_member(request, id):
    member = get_object_or_404(Member, id=id)
    request.session['form_data_edit_member'] = request.POST

    if request.method == 'POST':
        form = MemberEditForm(request.POST, instance=member)

        if form.is_valid():
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            full_name = form.cleaned_data['full_name']
            is_active = form.cleaned_data['is_active'] 
            
            member.email = email
            member.phone = phone
            member.full_name = full_name
            member.is_active = is_active
            member.save()
            
            messages.success(request, 'Membro atualizado com sucesso!')
            request.session.pop('form_data_edit_member', None)
            return redirect('admin_panel:members')
        else:
            messages.error(request, 'Erro ao atualizar o membro. Verifique os dados e tente novamente.')
            return redirect('admin_panel:edit_member_view', id=id)
        
    else:
        return redirect('admin_panel:members')

@login_required
def add_payment(request, id):
    member = get_object_or_404(Member, id=id)
    
    request.session['form_data_add_payment'] = request.POST
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        
        if form.is_valid():
            form.save(member=member)
            messages.success(request, 'Pagamento adicionado com sucesso!')
            del request.session['form_data_add_payment']
            return redirect('admin_panel:members')
        else:
            messages.error(request, 'Erro ao adicionar pagamento. Verifique os dados e tente novamente.')
            return redirect('admin_panel:add_payment_view', id=id)
    else:
        return redirect('admin_panel:add_payment_view', id=id)


import plotly.express as px
import pandas as pd

@login_required
def finance(request):
    current_year_profit = Payment.get_current_year_profit()
    current_month_profit = Payment.get_current_month_profit()
    
    months_profit = {
        'Janeiro': Payment.get_monthly_profit(1),
        'Fevereiro': Payment.get_monthly_profit(2),
        'Março': Payment.get_monthly_profit(3),
        'Abril': Payment.get_monthly_profit(4),
        'Maio': Payment.get_monthly_profit(5),
        'Junho': Payment.get_monthly_profit(6),
        'Julho': Payment.get_monthly_profit(7),
        'Agosto': Payment.get_monthly_profit(8),
        'Setembro': Payment.get_monthly_profit(9),
        'Outubro': Payment.get_monthly_profit(10),
        'Novembro': Payment.get_monthly_profit(11),
        'Dezembro': Payment.get_monthly_profit(12),
    }
    
    df = pd.DataFrame(list(months_profit.items()), columns=['Month', 'Profit'])
    
    fig = px.bar(df, x='Month', y='Profit', title="Lucro Mensal", labels={'Month': 'Mês', 'Profit': 'Lucro'})
    
    graph_html = fig.to_html(full_html=False)
        
    month_with_highest_profit = max(months_profit, key=lambda month: months_profit[month])
    
    recents_payments = Payment.objects.order_by('-payment_date').select_related('member')[:12]
    
    
    context = {
        'current_year_profit': current_year_profit,
        'current_month_profit': current_month_profit,
        'months_profit': months_profit,
        'month_with_highest_profit': month_with_highest_profit,
        'recents_payments': recents_payments,
        'graph_html': graph_html
    }
    
    
    return render(request, 'admin_panel/pages/finance.html', context)


from django.db.models import Sum
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.views.decorators.http import require_GET

@login_required
@require_GET
def generate_pdf_general_report(request):
    active_members = Member.objects.filter(is_active=True).count()
    inactive_members =Member.objects.filter(is_active=False).count()
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0.00
    payments = Payment.objects.select_related('member').all()
    
    context = {
        'date': localtime().strftime('%Y-%m-%d %H:%M'),
        'active_members': active_members,
        'inactive_members': inactive_members,
        'total_revenue': total_revenue,
        'payments': payments
    }
    
    html_string = render_to_string('reports/gym_general_report.html', context)
    
    
    response = HttpResponse(content_type='application/pdf')
    file_name = f"gym_report_{localdate().strftime('%Y-%m-%d')}"
    response['Content-Disposition'] = f'attachment; filename={file_name}.pdf'
    
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    
    if pisa_status.err:
        messages.error(request, 'Erro ao gerar o PDF.')
        return redirect('admin_panel:finance')
    
    
    return response

from admin_panel.models import DailyReport

@login_required
@require_GET
def generate_pdf_report_of_current_day(request):
    report = DailyReport.objects.filter(date=localdate()).first()
    
    if not report:
        report = DailyReport.create_report()
        
    context = {
        'date': localtime().strftime('%Y-%m-%d %H:%M'),
        'active_members': report.active_students,
        'inactive_members': report.pending_students,
        'total_revenue': report.daily_profit,
        'payments': report.payments.all()
    }
    
    html_string = render_to_string('reports/gym_current_day_report.html', context)
    
    response = HttpResponse(content_type='application/pdf')
    file_name = f"gym_current_day_report_{localdate().strftime('%Y-%m-%d')}"
    response['Content-Disposition'] = f'attachment; filename={file_name}.pdf'
    
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    
    if pisa_status.err:
        messages.error(request, 'Erro ao gerar o PDF.')
        return redirect('admin_panel:finance')
    
    
    return response