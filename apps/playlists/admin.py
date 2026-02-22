from django.contrib import admin
from .models import Playlist, PlaylistItem, Watchlist

class PlaylistItemInline(admin.TabularInline):
    model = PlaylistItem
    extra = 0

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_public', 'item_count', 'created_at']
    inlines = [PlaylistItemInline]

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'added_at']
