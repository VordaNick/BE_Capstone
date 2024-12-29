from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from .views import(
     BookViewSet,TransactionViewset,NotificationListView,
     NotificationCreateView, UserProfileView, UserRegistrationView,
     Reviews, BookRequestView, GeneralNotificationView
)

router = DefaultRouter()
router.register('books', BookViewSet, basename='books')
router.register(r'reviews', Reviews, basename='review')

transaction_view = TransactionViewset.as_view({
    'post': 'create',
    'patch': 'return_book'
})


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name="obtain_token"),
    path('token/refresh/', TokenRefreshView.as_view(), name="refresh_token"),
    path('', include(router.urls)),
    path('transactions/', transaction_view, name='transactions'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('requests/', BookRequestView.as_view(), name='book-requests'),
    path('notifications/', NotificationListView.as_view(), name='user-notifications'),
    path('notifications/create/', NotificationCreateView.as_view(), name='create_notifications'),
    path('notifications/general/', GeneralNotificationView.as_view(), name='general-notifications')
]
