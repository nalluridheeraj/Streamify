from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDay, TruncMonth
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
import json
from datetime import timedelta, date

from .decorators import admin_required
from apps.users.models import User
from apps.content.models import Content, Genre, Comment, Like
from apps.subscriptions.models import Plan, Subscription
from apps.payments.models import Payment


# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────

def admin_login_view(request):
    if request.user.is_authenticated and (request.user.is_admin or request.user.is_staff):
        return redirect('admin_panel:dashboard')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, email=email, password=password)
        if user and (user.is_admin or user.is_staff):
            login(request, user)
            return redirect('admin_panel:dashboard')
        messages.error(request, 'Invalid credentials or insufficient privileges.')
    return render(request, 'admin_panel/login.html')


@admin_required
def admin_logout_view(request):
    logout(request)
    return redirect('admin_panel:login')


# ──────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────

@admin_required
def dashboard_view(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    # KPIs
    total_users = User.objects.count()
    new_users_30d = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    total_content = Content.objects.count()
    published_content = Content.objects.filter(is_published=True).count()
    active_subs = Subscription.objects.filter(status='active', end_date__gte=now.date()).count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(t=Sum('amount'))['t'] or 0
    revenue_30d = Payment.objects.filter(status='completed', payment_date__gte=thirty_days_ago).aggregate(t=Sum('amount'))['t'] or 0

    # User growth chart data (last 30 days)
    user_growth = list(
        User.objects.filter(date_joined__gte=thirty_days_ago)
        .annotate(day=TruncDay('date_joined'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
        .values_list('day', 'count')
    )

    # Revenue chart (last 30 days)
    revenue_chart = list(
        Payment.objects.filter(status='completed', payment_date__gte=thirty_days_ago)
        .annotate(day=TruncDay('payment_date'))
        .values('day')
        .annotate(total=Sum('amount'))
        .order_by('day')
        .values_list('day', 'total')
    )

    # Content by type
    content_by_type = list(
        Content.objects.values('content_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Recent activity
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_payments = Payment.objects.filter(status='completed').order_by('-payment_date').select_related('user', 'subscription__plan')[:5]
    recent_content = Content.objects.order_by('-uploaded_at').select_related('uploaded_by')[:5]

    # Top content
    top_content = Content.objects.filter(is_published=True).order_by('-view_count')[:5]

    context = {
        'total_users': total_users,
        'new_users_30d': new_users_30d,
        'total_content': total_content,
        'published_content': published_content,
        'active_subs': active_subs,
        'total_revenue': float(total_revenue),
        'revenue_30d': float(revenue_30d),
        'user_growth_json': json.dumps([{'day': str(d.date()), 'count': c} for d, c in user_growth]),
        'revenue_chart_json': json.dumps([{'day': str(d.date()), 'total': float(t)} for d, t in revenue_chart]),
        'content_by_type_json': json.dumps(content_by_type),
        'recent_users': recent_users,
        'recent_payments': recent_payments,
        'recent_content': recent_content,
        'top_content': top_content,
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ──────────────────────────────────────────────
# USERS
# ──────────────────────────────────────────────

@admin_required
def users_list_view(request):
    q = request.GET.get('q', '')
    role = request.GET.get('role', '')
    qs = User.objects.annotate(
        content_count=Count('uploaded_content', distinct=True),
        payment_count=Count('payments', distinct=True),
    ).order_by('-date_joined')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q))
    if role:
        qs = qs.filter(role=role)
    paginator = Paginator(qs, 20)
    users = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'admin_panel/users.html', {
        'users': users, 'q': q, 'role': role,
        'total_count': qs.count(),
    })


@admin_required
def user_detail_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    subscriptions = user.subscriptions.all().order_by('-created_at')
    payments = user.payments.all().order_by('-payment_date')[:10]
    content = user.uploaded_content.all().order_by('-uploaded_at')[:10]
    return render(request, 'admin_panel/user_detail.html', {
        'target_user': user,
        'subscriptions': subscriptions,
        'payments': payments,
        'content': content,
    })


@admin_required
@require_POST
def toggle_user_active_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        return JsonResponse({'error': 'Cannot deactivate yourself'}, status=400)
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    return JsonResponse({'active': user.is_active, 'name': user.name})


@admin_required
@require_POST
def change_user_role_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    new_role = request.POST.get('role')
    if new_role in ('user', 'creator', 'admin'):
        user.role = new_role
        if new_role == 'admin':
            user.is_staff = True
        user.save(update_fields=['role', 'is_staff'])
        messages.success(request, f'Role updated to {new_role} for {user.name}.')
    return redirect('admin_panel:user_detail', pk=pk)


# ──────────────────────────────────────────────
# CONTENT
# ──────────────────────────────────────────────

@admin_required
def content_list_view(request):
    q = request.GET.get('q', '')
    ctype = request.GET.get('type', '')
    status = request.GET.get('status', '')
    qs = Content.objects.select_related('uploaded_by').order_by('-uploaded_at')
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(artist_name__icontains=q))
    if ctype:
        qs = qs.filter(content_type=ctype)
    if status == 'published':
        qs = qs.filter(is_published=True)
    elif status == 'draft':
        qs = qs.filter(is_published=False)
    elif status == 'premium':
        qs = qs.filter(is_premium=True)
    paginator = Paginator(qs, 25)
    content = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'admin_panel/content.html', {
        'content': content, 'q': q, 'ctype': ctype, 'status': status,
        'total_count': qs.count(),
    })


@admin_required
@require_POST
def toggle_publish_view(request, pk):
    content = get_object_or_404(Content, pk=pk)
    content.is_published = not content.is_published
    content.save(update_fields=['is_published'])
    return JsonResponse({'published': content.is_published, 'title': content.title})


@admin_required
@require_POST
def delete_content_view(request, pk):
    content = get_object_or_404(Content, pk=pk)
    title = content.title
    content.delete()
    messages.success(request, f'"{title}" deleted.')
    return redirect('admin_panel:content')


# ──────────────────────────────────────────────
# SUBSCRIPTIONS & PLANS
# ──────────────────────────────────────────────

@admin_required
def subscriptions_view(request):
    now = timezone.now()
    qs = Subscription.objects.select_related('user', 'plan').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)
    paginator = Paginator(qs, 25)
    subscriptions = paginator.get_page(request.GET.get('page', 1))

    # Stats
    stats = {
        'active': Subscription.objects.filter(status='active', end_date__gte=now.date()).count(),
        'expired': Subscription.objects.filter(status='expired').count(),
        'cancelled': Subscription.objects.filter(status='cancelled').count(),
    }
    plans = Plan.objects.annotate(sub_count=Count('subscription')).all()

    return render(request, 'admin_panel/subscriptions.html', {
        'subscriptions': subscriptions,
        'stats': stats,
        'plans': plans,
        'status_filter': status_filter,
    })


@admin_required
def plans_view(request):
    plans = Plan.objects.annotate(sub_count=Count('subscription')).all()
    return render(request, 'admin_panel/plans.html', {'plans': plans})


@admin_required
def edit_plan_view(request, pk=None):
    plan = get_object_or_404(Plan, pk=pk) if pk else None
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        price = request.POST.get('price', '0')
        duration = request.POST.get('duration_days', '30')
        description = request.POST.get('description', '')
        features_raw = request.POST.get('features', '')
        features = [f.strip() for f in features_raw.split('\n') if f.strip()]
        is_active = request.POST.get('is_active') == 'on'
        if plan:
            plan.name = name
            plan.slug = slug
            plan.price = price
            plan.duration_days = duration
            plan.description = description
            plan.features = features
            plan.is_active = is_active
            plan.save()
            messages.success(request, 'Plan updated.')
        else:
            Plan.objects.create(
                name=name, slug=slug, price=price, duration_days=duration,
                description=description, features=features, is_active=is_active
            )
            messages.success(request, 'Plan created.')
        return redirect('admin_panel:plans')
    return render(request, 'admin_panel/edit_plan.html', {'plan': plan})


@admin_required
@require_POST
def delete_plan_view(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    plan.delete()
    messages.success(request, f'Plan "{plan.name}" deleted.')
    return redirect('admin_panel:plans')


# ──────────────────────────────────────────────
# PAYMENTS
# ──────────────────────────────────────────────

@admin_required
def payments_view(request):
    qs = Payment.objects.select_related('user', 'subscription__plan').order_by('-payment_date')
    status_filter = request.GET.get('status', '')
    q = request.GET.get('q', '')
    if status_filter:
        qs = qs.filter(status=status_filter)
    if q:
        qs = qs.filter(Q(user__email__icontains=q) | Q(user__name__icontains=q))
    paginator = Paginator(qs, 25)
    payments = paginator.get_page(request.GET.get('page', 1))
    total_revenue = Payment.objects.filter(status='completed').aggregate(t=Sum('amount'))['t'] or 0
    return render(request, 'admin_panel/payments.html', {
        'payments': payments,
        'total_revenue': total_revenue,
        'status_filter': status_filter,
        'q': q,
    })


# ──────────────────────────────────────────────
# GENRES
# ──────────────────────────────────────────────

@admin_required
def genres_view(request):
    genres = Genre.objects.annotate(content_count=Count('content')).order_by('name')
    return render(request, 'admin_panel/genres.html', {'genres': genres})


@admin_required
def edit_genre_view(request, pk=None):
    genre = get_object_or_404(Genre, pk=pk) if pk else None
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        description = request.POST.get('description', '')
        if genre:
            genre.name = name
            genre.slug = slug
            genre.description = description
            genre.save()
            messages.success(request, 'Genre updated.')
        else:
            Genre.objects.create(name=name, slug=slug, description=description)
            messages.success(request, 'Genre created.')
        return redirect('admin_panel:genres')
    return render(request, 'admin_panel/edit_genre.html', {'genre': genre})


@admin_required
@require_POST
def delete_genre_view(request, pk):
    genre = get_object_or_404(Genre, pk=pk)
    genre.delete()
    messages.success(request, f'Genre "{genre.name}" deleted.')
    return redirect('admin_panel:genres')


# ──────────────────────────────────────────────
# COMMENTS MODERATION
# ──────────────────────────────────────────────

@admin_required
def comments_view(request):
    qs = Comment.objects.select_related('user', 'content').order_by('-created_at')
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(text__icontains=q) | Q(user__name__icontains=q))
    paginator = Paginator(qs, 30)
    comments = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'admin_panel/comments.html', {'comments': comments, 'q': q})


@admin_required
@require_POST
def delete_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return JsonResponse({'deleted': True})


# ──────────────────────────────────────────────
# API: Stats for charts
# ──────────────────────────────────────────────

@admin_required
def api_stats_view(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    user_growth = list(
        User.objects.filter(date_joined__gte=thirty_days_ago)
        .annotate(day=TruncDay('date_joined'))
        .values('day').annotate(count=Count('id')).order_by('day')
    )
    revenue = list(
        Payment.objects.filter(status='completed', payment_date__gte=thirty_days_ago)
        .annotate(day=TruncDay('payment_date'))
        .values('day').annotate(total=Sum('amount')).order_by('day')
    )
    return JsonResponse({
        'user_growth': [{'day': str(r['day'].date()), 'count': r['count']} for r in user_growth],
        'revenue': [{'day': str(r['day'].date()), 'total': float(r['total'])} for r in revenue],
    })
