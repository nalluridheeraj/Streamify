from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard_view, name='dashboard'),

    # Users
    path('users/', views.users_list_view, name='users'),
    path('users/<int:pk>/', views.user_detail_view, name='user_detail'),
    path('users/<int:pk>/toggle-active/', views.toggle_user_active_view, name='toggle_user_active'),
    path('users/<int:pk>/change-role/', views.change_user_role_view, name='change_user_role'),

    # Content
    path('content/', views.content_list_view, name='content'),
    path('content/<int:pk>/toggle-publish/', views.toggle_publish_view, name='toggle_publish'),
    path('content/<int:pk>/delete/', views.delete_content_view, name='delete_content'),

    # Subscriptions
    path('subscriptions/', views.subscriptions_view, name='subscriptions'),

    # Plans
    path('plans/', views.plans_view, name='plans'),
    path('plans/create/', views.edit_plan_view, name='create_plan'),
    path('plans/<int:pk>/edit/', views.edit_plan_view, name='edit_plan'),
    path('plans/<int:pk>/delete/', views.delete_plan_view, name='delete_plan'),

    # Payments
    path('payments/', views.payments_view, name='payments'),

    # Genres
    path('genres/', views.genres_view, name='genres'),
    path('genres/create/', views.edit_genre_view, name='create_genre'),
    path('genres/<int:pk>/edit/', views.edit_genre_view, name='edit_genre'),
    path('genres/<int:pk>/delete/', views.delete_genre_view, name='delete_genre'),

    # Comments
    path('comments/', views.comments_view, name='comments'),
    path('comments/<int:pk>/delete/', views.delete_comment_view, name='delete_comment'),

    # API
    path('api/stats/', views.api_stats_view, name='api_stats'),
]
