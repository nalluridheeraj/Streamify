from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Playlist, PlaylistItem, Watchlist
from apps.content.models import Content


@login_required
def playlist_list_view(request):
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'playlists/list.html', {'playlists': playlists})


@login_required
def playlist_detail_view(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    if not playlist.is_public and playlist.user != request.user:
        messages.error(request, 'You do not have access to this playlist.')
        return redirect('playlists:list')
    items = playlist.items.select_related('content')
    return render(request, 'playlists/detail.html', {'playlist': playlist, 'items': items})


@login_required
def create_playlist_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'on'
        if name:
            playlist = Playlist.objects.create(
                user=request.user, name=name,
                description=description, is_public=is_public
            )
            messages.success(request, f'Playlist "{name}" created.')
            return redirect('playlists:detail', pk=playlist.pk)
    return render(request, 'playlists/create.html')


@login_required
def delete_playlist_view(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk, user=request.user)
    if request.method == 'POST':
        playlist.delete()
        messages.success(request, 'Playlist deleted.')
        return redirect('playlists:list')
    return render(request, 'playlists/delete_confirm.html', {'playlist': playlist})


@login_required
def add_to_playlist_view(request, content_pk):
    content = get_object_or_404(Content, pk=content_pk)
    if request.method == 'POST':
        playlist_id = request.POST.get('playlist_id')
        playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
        PlaylistItem.objects.get_or_create(playlist=playlist, content=content)
        messages.success(request, f'Added to "{playlist.name}".')
    return redirect('content:detail', pk=content_pk)


@login_required
def remove_from_playlist_view(request, playlist_pk, content_pk):
    playlist = get_object_or_404(Playlist, pk=playlist_pk, user=request.user)
    PlaylistItem.objects.filter(playlist=playlist, content_id=content_pk).delete()
    messages.success(request, 'Removed from playlist.')
    return redirect('playlists:detail', pk=playlist_pk)


@login_required
def toggle_watchlist_view(request, content_pk):
    content = get_object_or_404(Content, pk=content_pk)
    wl, created = Watchlist.objects.get_or_create(user=request.user, content=content)
    if not created:
        wl.delete()
        saved = False
    else:
        saved = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'saved': saved})
    messages.success(request, 'Saved to watchlist.' if saved else 'Removed from watchlist.')
    return redirect('content:detail', pk=content_pk)


@login_required
def watchlist_view(request):
    items = Watchlist.objects.filter(user=request.user).select_related('content')
    return render(request, 'playlists/watchlist.html', {'items': items})
