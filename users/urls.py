from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login_view'),
    path('login/submit/', views.login_submit, name='login_submit'),
    path('logout/', views.logout_view , name='logout_view'),
    
    path('password/reset/', views.password_reset, name='password_reset'),
    path('password/reset/send/', views.password_reset_send, name='password_reset_send'),
    
    path('password/reset/confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password/reset/complete/', views.password_reset_complete, name='password_reset_complete'), 
]
