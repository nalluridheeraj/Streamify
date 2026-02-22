from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import RegisterAPIView, LoginAPIView, ProfileAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileAPIView.as_view(), name='api_profile'),
]
