import os
import mimetypes
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import Http404

# --- THE FIX: Custom view to handle video range requests locally ---
def ranged_media_serve(request, path, document_root=None):
    from ranged_response import RangedFileResponse
    
    # Securely resolve the file path
    document_root = os.path.abspath(document_root)
    fullpath = os.path.normpath(os.path.join(document_root, path.lstrip('/')))
    
    # Check if file exists and is safely inside the media folder
    if not fullpath.startswith(document_root) or not os.path.exists(fullpath):
        raise Http404("File not found")
        
    # Guess the content type (e.g., video/mp4)
    content_type, _ = mimetypes.guess_type(fullpath)
    content_type = content_type or 'application/octet-stream'
    
    # Return the special ranged response
    return RangedFileResponse(request, open(fullpath, 'rb'), content_type=content_type)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.content.urls', namespace='content')),
    path('users/', include('apps.users.urls', namespace='users')),
    path('subscriptions/', include('apps.subscriptions.urls', namespace='subscriptions')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('playlists/', include('apps.playlists.urls', namespace='playlists')),
    path('search/', include('apps.search.urls', namespace='search')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),
    path('admin-panel/', include('apps.admin_panel.urls', namespace='admin_panel')),
    path('accounts/', include('accounts.urls')),
    # API endpoints
    path('api/v1/', include([
        path('users/', include('apps.users.api_urls')),
        path('content/', include('apps.content.api_urls')),
        path('subscriptions/', include('apps.subscriptions.api_urls')),
    ])),
]

if settings.DEBUG:
    # 1. Route media files through our new ranged_media_serve view
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', ranged_media_serve, {'document_root': settings.MEDIA_ROOT}),
    ]
    
    # 2. Keep standard static files setup for CSS/JS
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)