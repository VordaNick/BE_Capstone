from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.timezone import now, timedelta
from django.core.validators import MinValueValidator, MaxValueValidator # For my Review Ratings, so ratings are between 1 to 5

# Defining a function to calculate expected date of return in my Transaction model
def calc_expected_return_date():
    return now() + timedelta(days=14)

# Creating a UserManager to handle my CustomUser Creation
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('date_of_membership', now())
        user = self.model(username=username, email=email, **extra_fields)
        
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

# Creating a CustomUser model because of the date_of_membership and is_active requirements
class CustomUser(AbstractUser):
    date_of_membership = models.DateField(auto_now_add=True, editable=False)
    is_active = models.BooleanField(default=True)
    bio = models.TextField(blank=True, null=True) # So members can say a little about themselves, the genre of books they like etc. When I become really good, I will include a function to recommend books to users based on the genre they like.
    # No need to add other fields as AbstractUser already has them
    
    objects = CustomUserManager()
    def __str__(self):
        return self.username
    
class Book(models.Model):
    title = models.CharField(max_length=150)
    author = models.CharField(max_length=150)
    isbn = models.CharField(max_length=13, unique=True)
    genre = models.CharField(max_length=100)
    published_date = models.DateField()
    available_copies = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title #So the string representation of the model is title
    
class Transaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='transactions')
    checkout_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField(default=calc_expected_return_date) #Every book borrowed should have an expected return date which is auto generated to be two weeks from the date of checkout
    return_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.username} - {self.book.title}'
    

class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Notification for {self.recipient.username}: {self.message[:50]}'
    
class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    review_text = models.TextField()
    rating = models.PositiveBigIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ['book', 'user']
    
    def __str__(self):
        return f'Review by {self.user.username} for {self.book.title}'
    
    
class BookRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='book_requests')
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.title} by {self.author} requested by {self.user.username}'