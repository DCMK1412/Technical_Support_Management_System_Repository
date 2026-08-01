import token
from unicodedata import category

from django.conf.locale import da
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from .models import Ticket, Category

User = get_user_model()

class TicketModelTests(TestCase):

    def test_ticket_creation(self):
        category = Category.objects.create(name='Test Category')
        user = User.objects.create_user(username='testuser', password='testpassword')


        ticket = Ticket.objects.create(
            title = 'test ticket',
            description = 'This is a test ticket.',
            category = category,
            created_by = user,
        )

        self.assertEqual(ticket.title, 'test ticket')
        self.assertEqual(ticket.status, 'OPEN')


class TicketViewTests(TestCase):

    def test_unauthenticated_user_cannot_access_tickets(self):
        url = reverse('tickets:ticket-list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [401, 403])  


    def test_login_api_view(self):
        User.objects.create_user(username="testuser", password="password123")

        url = reverse('tickets:auth-login')
        data = {
            "username": "testuser",
            "password": "password123"
        }
        response = self.client.post(url, data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())



    def test_Login_with_invalid_password(self):
        User.objects.create_user(username="testuser", password="password123")

        url = reverse('tickets:auth-login')
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(url, data, content_type='application/json')


    def test_antheniticated_user_can_create_ticket(self):
        user = User.objects.create_user(username='testuser', password='correctpassword')
        category = Category.objects.create(name='Test Category')
        token = Token.objects.create(user=user)

        url = reverse('tickets:ticket-list')
        data = {
            'title': 'New API Ticket',
            'description': 'test',
            'category': category.id
        }

        response = self.client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION= f"Token {token.key}")

        self.assertEqual(response.status_code, 201) 
        self.assertEqual(Ticket.objects.count(),1)
        self.assertEqual(Ticket.objects.first().title, 'New API Ticket')


    def test_update_ticket_status(self):
        user = User.objects.create_user(username='supportuser', password='correctpassword')
        category = Category.objects.create(name='test')
        ticket = Ticket.objects.create(title='test', description='test', category=category, created_by=user, status='OPEN')
        token = Token.objects.create(user=user)

        url = reverse('tickets:ticket-detail', kwargs={'pk': ticket.pk})
        data = {'status': 'IN_PROGRESS'}

        response = self.client.patch(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Token {token.key}')

        self.assertEqual(response.status_code, 200)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'IN_PROGRESS')


    def test_user_cannot_update_other_tickets(self):
        user1 = User.objects.create_user(username='user1', password='password1', role="USER")
        user2 = User.objects.create_user(username='user2', password='password2', role="USER")
        category = Category.objects.create(name='Test Category')
        ticket = Ticket.objects.create(title='User1 Ticket', description='Ticket by user1', category=category, created_by=user1, status='OPEN')
        token2 = Token.objects.create(user=user2)

        url = reverse('tickets:ticket-detail', kwargs={'pk': ticket.pk})
        data = {'status': 'CLOSED'}

        response = self.client.patch(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Token {token2.key}')

        self.assertIn(response.status_code, [403, 404])  
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'OPEN')
        self.assertEqual(ticket.title, 'User1 Ticket')
        