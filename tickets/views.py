from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Ticket, Category

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import TicketSerializer, CategorySerializer
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

class TicketList(APIView):
    def get(self, request, format=None):
        tickets = Ticket.objects.all()
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TicketDetail(APIView):
    def get_object(self, pk):
        try:
            return Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return None

    def get(self, request, pk, format=None):
        ticket = self.get_object(pk)
        if ticket is None:
            return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        ticket = self.get_object(pk)
        if ticket is None:
            return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = TicketSerializer(ticket, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk, format=None):
        ticket = self.get_object(pk)
        if ticket is None:
            return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TicketSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        ticket = self.get_object(pk)
        if ticket is None:
            return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
            
        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class CategoryList(APIView):
    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CategoryDetail(APIView):
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk, format=None):
        category = self.get_object(pk)
        if category is None:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        category = self.get_object(pk)
        if category is None:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        category = self.get_object(pk)
        if category is None:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
            
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)