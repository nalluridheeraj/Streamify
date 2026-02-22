from django.contrib import admin
from .models import Content, Comment, Genre, Like, ContentView


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'uploaded_by', 'is_published', 'is_premium', 'view_count', 'uploaded_at']
    list_filter = ['content_type', 'is_published', 'is_premium', 'genre']
    search_fields = ['title', 'artist_name', 'description']
    list_editable = ['is_published', 'is_premium']
    filter_horizontal = ['genre']
    date_hierarchy = 'uploaded_at'
    readonly_fields = ['view_count', 'uploaded_at', 'updated_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'user__email']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'created_at']
