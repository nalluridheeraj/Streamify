from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ContentViewSet

router = DefaultRouter()
router.register(r'', ContentViewSet, basename='content')

urlpatterns = [
    path('', include(router.urls)),
]
