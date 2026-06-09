from django.urls import path
from . import views
from .views import RegisterView, register_ui

app_name = 'tickets'

urlpatterns = [
    path('login-ui/', views.login_page, name='login-ui'),
    path('tickets-ui/', views.tickets_page, name='tickets-ui'),
    
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('tickets/', views.TicketList.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', views.TicketDetail.as_view(), name='ticket-detail'),

    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetail.as_view(), name='category-detail'),

    path('auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('auth/login/', views.LoginView.as_view(), name='auth-login'),

    path('register-ui/', register_ui, name='register-ui'),
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
]