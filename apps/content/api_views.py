from rest_framework import serializers, viewsets, permissions, filters

from .models import Content, Comment, Genre, Like


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug']


class ContentSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.name', read_only=True)
    like_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    duration_display = serializers.ReadOnlyField()

    class Meta:
        model = Content
        fields = ['id', 'title', 'description', 'content_type', 'file_path', 'thumbnail',
                  'duration', 'duration_display', 'genre', 'artist_name', 'album',
                  'is_premium', 'view_count', 'like_count', 'comment_count',
                  'uploaded_by_name', 'uploaded_at']


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user_name', 'text', 'created_at', 'parent']
        read_only_fields = ['user_name', 'created_at']


class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Content.objects.filter(is_published=True)
    serializer_class = ContentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'artist_name', 'album']
    ordering_fields = ['uploaded_at', 'view_count', 'title']
    ordering = ['-uploaded_at']

    def get_queryset(self):
        qs = super().get_queryset()
        content_type = self.request.query_params.get('type')
        genre = self.request.query_params.get('genre')
        if content_type:
            qs = qs.filter(content_type=content_type)
        if genre:
            qs = qs.filter(genre__slug=genre)
        return qs
