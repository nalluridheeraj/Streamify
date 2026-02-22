from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from apps.content.models import Content, ContentView
from apps.payments.models import Payment


@login_required
def creator_analytics_view(request):
    if not request.user.is_creator:
        from django.shortcuts import redirect
        return redirect('content:home')
    my_content = Content.objects.filter(uploaded_by=request.user)
    total_views = ContentView.objects.filter(content__in=my_content).count()
    top_content = my_content.order_by('-view_count')[:10]
    monthly_views = (
        ContentView.objects
        .filter(content__in=my_content)
        .annotate(month=TruncMonth('watched_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    context = {
        'my_content': my_content,
        'total_views': total_views,
        'top_content': top_content,
        'monthly_views': list(monthly_views),
        'total_content': my_content.count(),
    }
    return render(request, 'analytics/creator.html', context)


@login_required
def admin_analytics_view(request):
    if not request.user.is_admin:
        from django.shortcuts import redirect
        return redirect('content:home')
    from apps.users.models import User
    total_users = User.objects.count()
    total_content = Content.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    total_views = ContentView.objects.count()
    recent_payments = Payment.objects.filter(status='completed').order_by('-payment_date')[:10]
    context = {
        'total_users': total_users,
        'total_content': total_content,
        'total_revenue': total_revenue,
        'total_views': total_views,
        'recent_payments': recent_payments,
    }
    return render(request, 'analytics/admin.html', context)
