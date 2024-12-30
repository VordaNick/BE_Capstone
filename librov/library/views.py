from rest_framework import viewsets, status, generics, permissions, views
from rest_framework.response import Response
from .models import Book, Transaction, Notification, CustomUser, Review, BookRequest
from .serializers import(
     BookSerializer, ReviewSerializer, TransactionSerializer,
     NotificationSerializer, UserProfileSerializer,
     UserRegistrationSerializer, BookRequestSerializer, GeneralNotificationSerializer
)
from .permissions import IsStaffOrReadOnly, IsAuthorOrReadOnly
import datetime
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import serializers



class BookViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly] # This is a custom permission I created so that only staff can add, edit, or delete books
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['title', 'author', 'isbn', 'available_copies', 'genre']
    search_fields = ['title', 'author', 'isbn', 'genre']
    ordering_fields = ['title', 'published_date']
    
    
class TransactionViewset(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated] #So that only authenticated users can carry out transactions
    
    def create(self, request):
        #The logic that controls book checkout
        book_id = request.data.get('book_id')
        book = Book.objects.filter(id=book_id, available_copies__gt=0).first()
        if not book:
            return Response({'error': "Book is currently unavailable"}, status=status.HTTP_400_BAD_REQUEST) #To make sure only books with available copies can be checked out
        #Logic to ensure a user is unable to check out a book more than once
        user_transactions = Transaction.objects.filter(user=request.user, book=book, return_date=None)
        if user_transactions.exists():
            return Response({'error': 'You have already borrowed this book'}, status=status.HTTP_400_BAD_REQUEST)
        transaction = Transaction.objects.create(user=request.user, book=book) #Creating a transaction if user transaction does not exist
        book.available_copies -= 1 #Reducing the number of available copies if checkout transaction is created successfully
        book.save()
        return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
    
    #The Logic that controls Book Returning
    def return_book(self, request):
        transaction_id = request.data.get('transaction_id')
        # Logic to ensure you can only return a book you borrowed
        try:
            transaction = Transaction.objects.get(id=transaction_id, user=request.user)
        except Transaction.DoesNotExist:
            return Response({"error": "The Checkout transaction does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Logic to ensure a book can only be returned once
        if transaction.return_date is not None:
            return Response({"error": "This transaction has already been settled."}, status=status.HTTP_400_BAD_REQUEST)

        # If everything checks out, successfullly return the book
        transaction.return_date = datetime.datetime.now()
        transaction.save()
        book = transaction.book
        book.available_copies += 1 # Increase available copies
        book.save()

        return Response(TransactionSerializer(transaction).data, status=status.HTTP_200_OK)
    
    
class NotificationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
class NotificationCreateView(generics.CreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        recipient_id = self.request.data.get('recipient')
        try:
            recipient = CustomUser.objects.get(id=recipient_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({'recipient': "A User with that ID was not found"})
        serializer.save(recipient=recipient)
    
    
class UserProfileView(RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # Save the user

        # Logic to generate tokens for the user upon successful registration
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Return a welcome message and user tokens
        return Response(
            {
                "message": {
                    f"Welcome to Librov, your account has been successfully created and your User ID is {user.id}. Below is a token unique to your account, that you can use for authentication. If you need a new one, simply send a POST request with your username and password to library/tokens."
                },
                "tokens": {
                    "refresh": refresh_token,
                    "access": access_token,
                },
            },
            status=status.HTTP_201_CREATED,
        )
        
        
def homepage(request):
    return render(request, 'home.html')



class Reviews(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrReadOnly, permissions.IsAuthenticatedOrReadOnly]
    queryset = Review.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['book', 'user']
    ordering_fields = ['rating']
    

    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        book_id = request.data.get('book')
        user = request.user
        existing_review = Review.objects.filter(book_id=book_id, user=user).first() # Check if the user already has a review on this book
        if existing_review:
            serializer = self.get_serializer(existing_review, data=request.data, partial=True) # Get the review
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer) # Update the review
            return Response(serializer.data)
        return super().create(request, *args, **kwargs) # Otherwise, create a new one
    
    
class BookRequestView(generics.ListCreateAPIView):
    serializer_class = BookRequestSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return BookRequest.objects.all()
        return BookRequest.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    
class GeneralNotificationView(views.APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        serializer = GeneralNotificationSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.validated_data['message']
            recipients = CustomUser.objects.all()
            notifications = [
                Notification(recipient=user, message=message) for user in recipients
            ]
            Notification.objects.bulk_create(notifications)
            return Response({'detail': 'Notification sent to all users.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
             