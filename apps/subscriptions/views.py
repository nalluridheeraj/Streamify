from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Plan, Subscription


def plans_view(request):
    plans = Plan.objects.filter(is_active=True)
    current_sub = None
    if request.user.is_authenticated:
        current_sub = request.user.subscriptions.filter(
            status='active', end_date__gte=timezone.now().date()
        ).first()
    return render(request, 'subscriptions/plans.html', {
        'plans': plans,
        'current_subscription': current_sub
    })


@login_required
def subscribe_view(request, plan_slug):
    plan = get_object_or_404(Plan, slug=plan_slug, is_active=True)
    active_sub = request.user.subscriptions.filter(
        status='active', end_date__gte=timezone.now().date()
    ).first()
    if active_sub:
        messages.info(request, 'You already have an active subscription.')
        return redirect('subscriptions:my_subscription')
    return render(request, 'subscriptions/checkout.html', {'plan': plan})


@login_required
def my_subscription_view(request):
    subscriptions = request.user.subscriptions.all().order_by('-created_at')
    active_sub = subscriptions.filter(status='active', end_date__gte=timezone.now().date()).first()
    return render(request, 'subscriptions/my_subscription.html', {
        'subscriptions': subscriptions,
        'active_subscription': active_sub
    })


@login_required
def cancel_subscription_view(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    if request.method == 'POST':
        subscription.cancel()
        messages.success(request, 'Subscription cancelled.')
        return redirect('subscriptions:my_subscription')
    return render(request, 'subscriptions/cancel_confirm.html', {'subscription': subscription})
