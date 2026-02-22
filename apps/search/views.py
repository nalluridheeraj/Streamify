from django.shortcuts import render
from django.db.models import Q
from apps.content.models import Content, Genre
from apps.users.models import User


def search_view(request):
    query = request.GET.get('q', '').strip()
    content_type = request.GET.get('type', '')
    genre_slug = request.GET.get('genre', '')
    sort = request.GET.get('sort', 'relevance')

    results = Content.objects.filter(is_published=True)

    if query:
        results = results.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(artist_name__icontains=query) |
            Q(album__icontains=query)
        )

    if content_type:
        results = results.filter(content_type=content_type)

    if genre_slug:
        results = results.filter(genre__slug=genre_slug)

    if sort == 'popular':
        results = results.order_by('-view_count')
    elif sort == 'newest':
        results = results.order_by('-uploaded_at')
    elif sort == 'oldest':
        results = results.order_by('uploaded_at')
    else:
        results = results.order_by('-view_count')

    genres = Genre.objects.all()

    context = {
        'query': query,
        'results': results,
        'result_count': results.count(),
        'genres': genres,
        'content_type': content_type,
        'genre_slug': genre_slug,
        'sort': sort,
    }
    return render(request, 'search/results.html', context)
