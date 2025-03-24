from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Spotify callback and auth routes - match redirect URI exactly
    path('spotify/', include('core.urls.spotify_urls')),  # Now points to the correct module
    
    # Add the correct callback URL pattern
    path('core/spotify/callback/', RedirectView.as_view(pattern_name='spotify-callback'), name='spotify-callback-redirect'),
    
    # Core app URLs - using include with explicit app_name as a tuple
    path('', include(('core.urls', 'core'), namespace='core')),
    
    # API endpoints
    path('api/', include('api.urls', namespace='api')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
handler503 = 'core.views.service_unavailable'
