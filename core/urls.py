from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'core'  # This is the missing app_name attribute

urlpatterns = [
    # Main views
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('trends/', views.TrendsView.as_view(), name='trends'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('playlists/', views.PlaylistsView.as_view(), name='playlists'),
    path('playlists/<str:playlist_id>/', views.PlaylistDetailView.as_view(), name='playlist-detail'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Include Spotify-specific URLs from the separate module
    path('spotify/', include('core.urls.spotify_urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
handler503 = 'core.views.service_unavailable'