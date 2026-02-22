from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Content, Like, Comment, Genre, ContentView
from .forms import ContentUploadForm, CommentForm


def home_view(request):
    featured = Content.objects.filter(is_published=True).order_by('-view_count')[:6]
    recent_music = Content.objects.filter(is_published=True, content_type='music').order_by('-uploaded_at')[:8]
    recent_videos = Content.objects.filter(is_published=True, content_type='video').order_by('-uploaded_at')[:8]
    genres = Genre.objects.all()[:10]
    context = {
        'featured': featured,
        'recent_music': recent_music,
        'recent_videos': recent_videos,
        'genres': genres,
    }
    return render(request, 'content/home.html', context)


def content_list_view(request):
    content_type = request.GET.get('type', '')
    genre_slug = request.GET.get('genre', '')
    qs = Content.objects.filter(is_published=True)
    if content_type:
        qs = qs.filter(content_type=content_type)
    if genre_slug:
        qs = qs.filter(genre__slug=genre_slug)
    paginator = Paginator(qs, 20)
    page = request.GET.get('page', 1)
    content = paginator.get_page(page)
    genres = Genre.objects.all()
    context = {'content': content, 'genres': genres, 'content_type': content_type}
    return render(request, 'content/list.html', context)


def content_detail_view(request, pk):
    # Allow owner to see their own unpublished content
    if request.user.is_authenticated:
        content = get_object_or_404(
            Content,
            Q(pk=pk, is_published=True) | Q(pk=pk, uploaded_by=request.user)
        )
    else:
        content = get_object_or_404(Content, pk=pk, is_published=True)

    # Record view
    ContentView.objects.create(
        user=request.user if request.user.is_authenticated else None,
        content=content,
        ip_address=request.META.get('REMOTE_ADDR')
    )
    content.view_count += 1
    content.save(update_fields=['view_count'])

    user_liked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, content=content).exists()

    comments = content.comments.filter(parent=None).select_related('user')
    comment_form = CommentForm()
    related = Content.objects.filter(
        is_published=True, content_type=content.content_type
    ).exclude(pk=pk)[:6]

    # Check if user can stream (free content or active subscription)
    can_stream = not content.is_premium or (
        request.user.is_authenticated and request.user.has_active_subscription
    )

    context = {
        'content': content,
        'user_liked': user_liked,
        'comments': comments,
        'comment_form': comment_form,
        'related': related,
        'can_stream': can_stream,
    }
    return render(request, 'content/detail.html', context)


@login_required
def upload_content_view(request):
    if not request.user.is_creator:
        messages.error(request, 'You need a creator account to upload content.')
        return redirect('content:home')
    if request.method == 'POST':
        form = ContentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.uploaded_by = request.user
            content.save()
            form.save_m2m()
            messages.success(request, 'Content uploaded successfully!')
            return redirect('content:detail', pk=content.pk)
    else:
        form = ContentUploadForm()
    return render(request, 'content/upload.html', {'form': form})


@login_required
def edit_content_view(request, pk):
    content = get_object_or_404(Content, pk=pk, uploaded_by=request.user)
    if request.method == 'POST':
        form = ContentUploadForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, 'Content updated successfully!')
            return redirect('content:detail', pk=content.pk)
    else:
        form = ContentUploadForm(instance=content)
    return render(request, 'content/edit.html', {'form': form, 'content': content})


@login_required
def delete_content_view(request, pk):
    content = get_object_or_404(Content, pk=pk)
    if content.uploaded_by != request.user and not request.user.is_admin:
        return HttpResponseForbidden()
    if request.method == 'POST':
        content.delete()
        messages.success(request, 'Content deleted.')
        return redirect('content:list')
    return render(request, 'content/delete_confirm.html', {'content': content})


@login_required
def toggle_like_view(request, pk):
    if request.method == 'POST':
        content = get_object_or_404(Content, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, content=content)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return JsonResponse({'liked': liked, 'count': content.like_count})
    return JsonResponse({'error': 'Invalid method'}, status=405)


@login_required
def add_comment_view(request, pk):
    content = get_object_or_404(Content, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.content = content
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, pk=parent_id)
            comment.save()
            messages.success(request, 'Comment added.')
    return redirect('content:detail', pk=pk)


@login_required
def delete_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user and not request.user.is_admin:
        return HttpResponseForbidden()
    content_pk = comment.content.pk
    comment.delete()
    messages.success(request, 'Comment deleted.')
    return redirect('content:detail', pk=content_pk)

