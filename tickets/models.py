from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('SUPPORT', 'Support'),
        ('USER','User'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='USER')

    def __str__(self):
        return f"{self.username} - {self.role}"
    

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null = True)
    created_at= models.DateTimeField(auto_now_add= True) 

    class Meta:
        verbose_name_plural = "Categories"    #توحيد Categories مع Categorie

    def __str__(self):
        return self.name
    
class Ticket(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('WAITING_FOR_USER','Waiting_for_user'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
        )
    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField()

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tickets')
    created_by= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name= 'created_tickets')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,null = True, blank=True, related_name='assigned_tickets')

    status = models.CharField(max_length=20, choices= STATUS_CHOICES, default='OPEN')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='LOW')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket #{self.id}: {self.title}"
    
    

class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.ticket.id}"



class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='ticket_attachments/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.ticket.id}"
    