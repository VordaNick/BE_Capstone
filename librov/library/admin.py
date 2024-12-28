from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Book, Transaction, Review, BookRequest

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['id', 'username', 'email', 'date_of_membership', 'is_staff', 'is_active']
    readonly_fields = ['date_of_membership']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email', 'bio')}),
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'published_date', 'available_copies']
    search_fields = ['title', 'author', 'isbn']
    list_filter = ['available_copies']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'id', 'book', 'checkout_date', 'expected_return_date', 'return_date']
    search_fields = ['user__username', 'book__title']
    list_filter = ['return_date']
    
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'book', 'review_text', 'rating']
    search_fields = ['Book__title']
    
@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'author', 'created_at']