from django.db import models
from django.conf import settings
from apps.content.models import Content


class Playlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='playlists')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to='playlist_thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'playlists'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} by {self.user}"

    @property
    def item_count(self):
        return self.items.count()


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='items')
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position', 'added_at']
        unique_together = ('playlist', 'content')

    def __str__(self):
        return f"{self.playlist.name} - {self.content.title}"


class Watchlist(models.Model):
    """User's saved/bookmarked content"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content')
        ordering = ['-added_at']
