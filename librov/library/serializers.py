from rest_framework import serializers
from .models import Book,Transaction,Notification, Review, BookRequest, Notification
from django.contrib.auth import get_user_model
from django.db import models

CustomUser = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = ['password', 'username', 'email', 'bio']
        
        def create(self, validated_data):
            user = CustomUser.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                bio=validated_data['bio', '']
            )
            return user
        
class BookSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'isbn', 'published_date', 'available_copies', 'average_rating']
        
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return None

class TransactionSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'book_title', 'checkout_date', 'expected_return_date', 'return_date',]
        
        
        
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    book_title = serializers.CharField(source='book.title', read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'book',  'book_title', 'user', 'review_text', 'rating', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at', "book_title"]
        
class BookRequestSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = BookRequest
        fields = ['id', 'user', 'username', 'title', 'author', 'description', 'created_at']
        read_only_fields = ['user', 'username', 'created_at']
        
class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.ReadOnlyField(source='recipient.username')
    
    class Meta:
        model = Notification
        fields = ['recipient', 'message', 'created_at']
        read_only_fields = ['recipient', 'created_at']
        
        
class GeneralNotificationSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=255)
        

class UserProfileSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True,)
    notifications = NotificationSerializer(many=True, read_only=True)
    class Meta:
        model = CustomUser
        fields = ['username', 'id', 'email', 'date_of_membership', 'bio', 'notifications', 'transactions']
