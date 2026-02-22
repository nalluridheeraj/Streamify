from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.plans_view, name='plans'),
    path('subscribe/<slug:plan_slug>/', views.subscribe_view, name='subscribe'),
    path('my-subscription/', views.my_subscription_view, name='my_subscription'),
    path('cancel/<int:pk>/', views.cancel_subscription_view, name='cancel'),
]
