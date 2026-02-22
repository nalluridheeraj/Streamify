from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('creator/', views.creator_analytics_view, name='creator'),
    path('admin/', views.admin_analytics_view, name='admin'),
]
