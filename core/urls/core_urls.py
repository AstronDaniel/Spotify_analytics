from django.urls import path, include
from .. import views

app_name = 'core'

urlpatterns = [
    # Main views
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('trends/', views.TrendsView.as_view(), name='trends'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('playlists/', views.PlaylistsView.as_view(), name='playlists'),
    path('playlists/<str:playlist_id>/', views.PlaylistDetailView.as_view(), name='playlist-detail'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Spotify auth URLs
    path('spotify/login/', views.SpotifyLoginView.as_view(), name='spotify-login'),
    path('spotify/logout/', views.SpotifyLogoutView.as_view(), name='spotify-logout'),
    path('spotify/callback/', views.SpotifyCallbackView.as_view(), name='spotify-callback'),
]
