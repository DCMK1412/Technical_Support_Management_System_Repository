from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('api/tickets/', views.TicketList.as_view(), name='ticket-list'),
    path('api/tickets/<int:pk>/', views.TicketDetail.as_view(), name='ticket-detail'),
]