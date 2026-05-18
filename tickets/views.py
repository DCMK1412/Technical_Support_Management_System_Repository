from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Ticket, Category

# Create your views here.

@login_required
def admin_dashboard(request):
    total_tickets = Ticket.objects.count()

    open_tickets = Ticket.objects.filter(status='OPEN').count()
    in_progress_tickets = Ticket.objects.filter(status='IN_PROGRESS').count()
    waiting_tickets = Ticket.objects.filter(status='WAITING_FOR_USER').count()
    resolved_tickets = Ticket.objects.filter(status='RESOLVED').count()
    closed_tickets = Ticket.objects.filter(status='CLOSED').count()
    
    recent_tickets = Ticket.objects.order_by('-created_at')[:5]
    categories = Category.objects.all()
    
    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'waiting_tickets': waiting_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'recent_tickets': recent_tickets,
        'categories': categories,
    }
    
    return render(request, 'tickets/dashboard.html', context)