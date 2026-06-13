from rest_framework import serializers
from .models import Ticket, Category, TicketComment, TicketAttachment
from django.contrib.auth import get_user_model

User = get_user_model()

# Serializer for viewing user data (profile)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


# Serializer for creating a new account
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("The username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("The email is already registered.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role='USER'
        )
        return user



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']



class TicketCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = TicketComment
        fields = ['id', 'ticket', 'author', 'author_name', 'message', 'created_at']
        read_only_fields = ['author', 'created_at']
        extra_kwargs = {
            'ticket': {'required': False},
            'author': {'required': False}
        }



class TicketSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    assigned_to_name = serializers.ReadOnlyField(source='assigned_to.username')
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'created_by', 'created_by_name', 
            'assigned_to', 'assigned_to_name', 'category', 'category_name', 
            'status', 'priority', 'created_at', 'updated_at', 'comments'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    
    def get_comments(self, obj):
        comments = TicketComment.objects.filter(ticket=obj).order_by('-created_at')
        return TicketCommentSerializer(comments, many=True).data
    

class TicketAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.ReadOnlyField(source='uploaded_by.username')

    class Meta:
        model = TicketAttachment
        fields = ['id', 'ticket', 'file', 'uploaded_by', 'uploaded_by_name', 'uploaded_at']
        extra_kwargs = {
            'ticket': {'required': False},
            'uploaded_by': {'required': False}
        }