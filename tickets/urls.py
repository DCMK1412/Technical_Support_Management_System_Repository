from django.urls import path
from . import views
from .views import TicketAttachmentListCreateView

#app_name = 'tickets'

urlpatterns = [
    # UI
    path('login-ui/', views.login_page, name='login-ui'),
    path('register-ui/', views.register_ui, name='register-ui'),
    path('dashboard-ui/', views.dashboard_ui, name='dashboard-ui'), 
    path('tickets-ui/', views.tickets_page, name='tickets-ui'),
    path('tickets-detail-ui/', views.ticket_detail_ui, name='ticket-detail-ui'), 
    path('categories-ui/', views.categories_ui, name='categories-ui'), 
    path('users-ui/', views.users_ui, name='users-ui'),

    # APIs

    # Authentication APIs
    path('auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('auth/login/', views.LoginView.as_view(), name='auth-login'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth-logout'), 
    path('auth/profile/', views.ProfileView.as_view(), name='auth-profile'),
    #path('api/tickets/', views.TicketList.as_view()),

    path('api-dashboard/', views.DashboardAPIView.as_view(), name='api-dashboard'),

    path('api/tickets/', views.TicketList.as_view(), name='ticket-list'),
    path('api/tickets/<int:pk>/', views.TicketDetail.as_view(), name='ticket-detail'),

    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetail.as_view(), name='category-detail'),
    
    path('api/tickets/<int:pk>/comments/', views.CommentCreateView.as_view(), name='add-comment'),

    path('tickets/<int:ticket_id>/attachments/', TicketAttachmentListCreateView.as_view(), name='ticket-attachments'),

    # User Management APIs
    path('users/', views.UserAdminListView.as_view(), name='api_user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/role/', views.UserRoleUpdateView.as_view(), name='api_user_role_update'),

]
