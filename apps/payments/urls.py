from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<slug:plan_slug>/', views.checkout_view, name='checkout'),
    path('history/', views.payment_history_view, name='history'),
    path('detail/<int:pk>/', views.payment_detail_view, name='detail'),
    path('webhook/stripe/', views.stripe_webhook_view, name='stripe_webhook'),
]
