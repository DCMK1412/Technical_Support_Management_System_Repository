from django.urls import path
from . import views
from .views import TicketAttachmentListCreateView

app_name = 'tickets'

urlpatterns = [
    # UI
    path('login-ui/', views.login_page, name='login-ui'),
    path('register-ui/', views.register_ui, name='register-ui'),
    path('tickets-ui/', views.tickets_page, name='tickets-ui'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # APIs
    path('auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('auth/login/', views.LoginView.as_view(), name='auth-login'),


    path('tickets/', views.TicketList.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', views.TicketDetail.as_view(), name='ticket-detail'),
    
    path('tickets/<int:pk>/add_comment/', views.CommentCreateView.as_view(), name='add-comment'),

    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetail.as_view(), name='category-detail'),

    path('tickets/<int:ticket_id>/attachments/', TicketAttachmentListCreateView.as_view(), name='ticket-attachments'),

]
