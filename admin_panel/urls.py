from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.home, name='home'),
    
    path('members/', views.members, name='members'),
    path('members/edit/<int:id>/', views.edit_member_view, name='edit_member_view'),
    path('members/add-payment-view/<int:id>/', views.add_payment_view, name='add_payment_view'),
    
    path('finance/', views.finance, name='finance'),
    
    path('generate-general-report/', views.generate_pdf_general_report, name='generate_pdf_general_report'),
    path('generate-current-day-report/', views.generate_pdf_report_of_current_day, name='generate_pdf_report_of_current_day'),
    
    path('members/add/', views.add_member, name='add_member'),
    path('members/delete/<int:id>/', views.delete_member, name='delete_member'),
    path('members/edit/<int:id>/update/', views.edit_member, name='edit_member'),
    path('members/add-payment/<int:id>/', views.add_payment, name='add_payment')
]