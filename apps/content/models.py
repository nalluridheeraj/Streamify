from django.db import models
from django.conf import settings
from django.utils import timezone


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Content(models.Model):
    TYPE_CHOICES = [
        ('music', 'Music'),
        ('video', 'Video'),
        ('podcast', 'Podcast'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    file_path = models.FileField(upload_to='content/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    duration = models.PositiveIntegerField(help_text='Duration in seconds', default=0)
    genre = models.ManyToManyField(Genre, blank=True, related_name='content', db_table='content_genres')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_content'
    )
    artist_name = models.CharField(max_length=255, blank=True)
    album = models.CharField(max_length=255, blank=True)
    is_published = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False, help_text='Requires subscription')
    view_count = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} ({self.content_type})"

    @property
    def duration_display(self):
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content')

    def __str__(self):
        return f"{self.user} likes {self.content}"


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.content}"


class ContentView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content_views'
