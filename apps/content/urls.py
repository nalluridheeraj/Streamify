from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('browse/', views.content_list_view, name='list'),
    path('content/<int:pk>/', views.content_detail_view, name='detail'),
    path('upload/', views.upload_content_view, name='upload'),
    path('content/<int:pk>/edit/', views.edit_content_view, name='edit'),
    path('content/<int:pk>/delete/', views.delete_content_view, name='delete'),
    path('content/<int:pk>/like/', views.toggle_like_view, name='like'),
    path('content/<int:pk>/comment/', views.add_comment_view, name='comment'),
    path('comment/<int:pk>/delete/', views.delete_comment_view, name='delete_comment'),
    
]
