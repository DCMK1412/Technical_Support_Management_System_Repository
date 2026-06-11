from django.contrib import admin
from .models import User, Category, Ticket, TicketComment, TicketAttachment

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    search_fields = ('username', 'email')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'status', 'priority', 'created_by', 'assigned_to')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    list_editable = ('status', 'priority', 'assigned_to')

admin.site.register(TicketComment)
admin.site.register(TicketAttachment)
