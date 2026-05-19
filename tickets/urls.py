from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('tickets/', views.TicketList.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', views.TicketDetail.as_view(), name='ticket-detail'),

    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetail.as_view(), name='category-detail'),
]