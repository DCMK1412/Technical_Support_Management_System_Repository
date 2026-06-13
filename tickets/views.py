from django.shortcuts import render
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

from rest_framework import viewsets, permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Ticket, Category, TicketComment, TicketAttachment
from .serializers import (
    TicketSerializer, 
    CategorySerializer, 
    RegisterSerializer, 
    UserSerializer, 
    TicketCommentSerializer,
    TicketAttachmentSerializer
)

User = get_user_model()

def register_ui(request):
    return render(request, 'tickets/register.html')

# 1. Authentication Views (API)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                "user": UserSerializer(user).data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Please Enter username and password'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user) 
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful",
                "user": UserSerializer(user).data,
                "token": token.key
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Incorrect username or password'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)



# 2. Template Views (Dashboard)
def login_page(request):
    return render(request, 'tickets/login.html')

def tickets_page(request):
    return render(request, 'tickets/tickets.html')

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



# 3. Tickets Views (API)
class TicketList(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request, format=None):
        user = request.user
        
        if user.role == 'ADMIN':
            tickets = Ticket.objects.all()
        elif user.role == 'SUPPORT':
            tickets = Ticket.objects.filter(assigned_to=user)
        else:
            tickets = Ticket.objects.filter(created_by=user)

        # search and filter 
        search = request.query_params.get('search')
        ticket_status = request.query_params.get('status')
        priority = request.query_params.get('priority')
        category = request.query_params.get('category')

        if search:
            tickets = tickets.filter(title__icontains=search)
        if ticket_status:
            tickets = tickets.filter(status=ticket_status)
        if priority:
            tickets = tickets.filter(priority=priority)
        if category:
            tickets = tickets.filter(category_id=category)

        serializer = TicketSerializer(tickets.order_by('-created_at'), many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, status='OPEN')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TicketDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            ticket = Ticket.objects.get(pk=pk)

            if user.role == 'ADMIN':
                return ticket
            
            if user.role == 'USER':
                if ticket.created_by != user:
                    return None
                return ticket

            if user.role == 'SUPPORT':
                if ticket.assigned_to is not None and ticket.assigned_to != user:
                    return None  
                return ticket

            return None
        except Ticket.DoesNotExist:
            return None


    def get(self, request, pk, format=None):
        ticket = self.get_object(pk, request.user)
        if ticket is None:
            return Response({'error': 'Ticket not found or permission denied'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        return self.patch(request, pk, format)
    
    def patch(self, request, pk, format=None):
        ticket = self.get_object(pk, request.user)
        if ticket is None:
            return Response({'error': 'Ticket not found or permission denied'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user.role == 'USER' and ('priority' in request.data or 'assigned_to' in request.data):
            return Response({'error': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.user.role == 'SUPPORT':
            allowed_support_fields = {'status', 'priority', 'assigned_to'}
    
            if not set(request.data.keys()).issubset(allowed_support_fields):
                return Response({'error': 'Support agents can only update status or priority'}, status=status.HTTP_403_FORBIDDEN)

        serializer = TicketSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if request.user.role != 'ADMIN':
            return Response({'error': 'Admins only'}, status=status.HTTP_403_FORBIDDEN)
            
        ticket = self.get_object(pk, request.user)
        if ticket:
            ticket.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)



# 4. Categories Views (API)
class CategoryList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        if request.user.role != 'ADMIN':
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(APIView):
    permission_classes = [IsAuthenticated]

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
        if request.user.role != 'ADMIN':
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)
        
        category = self.get_object(pk)
        if category is None:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if request.user.role != 'ADMIN':
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)

        category = self.get_object(pk)
        if category is None:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
            
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
# 5. Comments Views (API)    
class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'USER' and ticket.created_by != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        comments = TicketComment.objects.filter(ticket=ticket)
        serializer = TicketCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
            
        if request.user.role == 'USER' and ticket.created_by != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = TicketCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ticket=ticket, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# 6. Attachments Views (API) 
class TicketAttachmentListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketAttachmentSerializer
    permission_classes = [IsAuthenticated]

    # 1. Fetch attachments for a specific ticket only
    def get_queryset(self):
        ticket_id = self.kwargs['ticket_id']
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        if self.request.user.role == 'USER' and ticket.created_by != self.request.user:
            raise PermissionDenied("authorization denied to view attachments for this ticket.")
            
        return TicketAttachment.objects.filter(ticket=ticket)

    # 2. Upload a new attachment and automatically link it to the ticket and user
    def perform_create(self, serializer):
        ticket_id = self.kwargs['ticket_id']
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        if self.request.user.role == 'USER' and ticket.created_by != self.request.user:
            raise PermissionDenied("you don't have permission to add attachments to this ticket.")
            
        serializer.save(ticket=ticket, uploaded_by=self.request.user)



# 7. User Management Views (API)
class UserAdminListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        if request.user.role != 'ADMIN':
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)
        users = User.objects.all().order_by('-date_joined')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserRoleUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, format=None):
        if request.user.role != 'ADMIN':
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user_to_update = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        new_role = request.data.get('role')
        if new_role and new_role in ['USER', 'SUPPORT', 'ADMIN']:
            user_to_update.role = new_role
            user_to_update.save()
            
        return Response(UserSerializer(user_to_update).data, status=status.HTTP_200_OK)
    
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        if request.user.role != 'ADMIN':
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
