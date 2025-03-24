from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'core'

urlpatterns = [
    # Public pages
    path('', views.HomeView.as_view(), name='home'),
    path('trends/', views.TrendsView.as_view(), name='trends'),
    path('about/', views.AboutView.as_view(), name='about'),
    
    # User dashboard
    path('app/', views.DashboardView.as_view(), name='dashboard'),
    path('app/playlists/', views.PlaylistsView.as_view(), name='playlists'),
    path('app/playlist/<str:playlist_id>/', views.PlaylistDetailView.as_view(), name='playlist-detail'),
    path('app/profile/', views.ProfileView.as_view(), name='profile'),
    
    # Spotify auth routes now in core/urls/spotify_urls.py
    # We keep these here for direct access, but they're also accessible via /spotify/
    path('spotify/callback/', views.SpotifyCallbackView.as_view(), name='spotify-callback'),
    path('spotify/login/', views.SpotifyLoginView.as_view(), name='spotify-login'),
    path('spotify/logout/', views.SpotifyLogoutView.as_view(), name='spotify-logout'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)