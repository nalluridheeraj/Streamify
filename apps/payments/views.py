from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from datetime import date, timedelta
from .models import Payment
from apps.subscriptions.models import Plan, Subscription

try:
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    STRIPE_AVAILABLE = True
except Exception:
    STRIPE_AVAILABLE = False


@login_required
def checkout_view(request, plan_slug):
    plan = get_object_or_404(Plan, slug=plan_slug, is_active=True)
    if request.method == 'POST':
        # Simulate payment processing (integrate Stripe in production)
        token = request.POST.get('stripeToken', '')
        try:
            # Create subscription
            today = date.today()
            subscription = Subscription.objects.create(
                user=request.user,
                plan=plan,
                status='active',
                start_date=today,
                end_date=today + timedelta(days=plan.duration_days),
            )
            # Record payment
            Payment.objects.create(
                user=request.user,
                subscription=subscription,
                amount=plan.price,
                status='completed',
                payment_method='stripe',
            )
            messages.success(request, f'Successfully subscribed to {plan.name}!')
            return redirect('subscriptions:my_subscription')
        except Exception as e:
            messages.error(request, f'Payment failed: {str(e)}')
    context = {
        'plan': plan,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def payment_history_view(request):
    payments = Payment.objects.filter(user=request.user)
    return render(request, 'payments/history.html', {'payments': payments})


@login_required
def payment_detail_view(request, pk):
    payment = get_object_or_404(Payment, pk=pk, user=request.user)
    return render(request, 'payments/detail.html', {'payment': payment})


@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    if not endpoint_secret:
        return JsonResponse({'status': 'no secret configured'}, status=400)
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    # Handle event types
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        Payment.objects.filter(stripe_payment_intent=intent['id']).update(status='completed')
    return JsonResponse({'status': 'success'})
