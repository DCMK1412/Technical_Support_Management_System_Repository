from rest_framework import serializers
from .models import Ticket, Category
from django.contrib.auth import get_user_model

User = get_user_model() 

class TicketSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(style={'base_template': 'textarea.html'}, required=False, allow_blank=True)
    priority = serializers.CharField(default='MEDIUM')
    status = serializers.CharField(default='OPEN')
    created_at = serializers.DateTimeField(read_only=True)
    
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def create(self, validated_data):
        return Ticket.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.status = validated_data.get('status', instance.status)
        instance.category = validated_data.get('category', instance.category)
        instance.created_by = validated_data.get('created_by', instance.created_by)
        instance.save()
        return instance