from django.urls import path
from . import views

app_name = 'playlists'

urlpatterns = [
    path('', views.playlist_list_view, name='list'),
    path('<int:pk>/', views.playlist_detail_view, name='detail'),
    path('create/', views.create_playlist_view, name='create'),
    path('<int:pk>/delete/', views.delete_playlist_view, name='delete'),
    path('add/<int:content_pk>/', views.add_to_playlist_view, name='add_to_playlist'),
    path('<int:playlist_pk>/remove/<int:content_pk>/', views.remove_from_playlist_view, name='remove_from_playlist'),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('watchlist/toggle/<int:content_pk>/', views.toggle_watchlist_view, name='toggle_watchlist'),
]
