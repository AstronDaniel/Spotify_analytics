# This file makes the urls directory a Python package
from django.urls import path
from .. import views

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
    
    # Spotify auth routes
    path('spotify/callback/', views.SpotifyCallbackView.as_view(), name='spotify-callback'),
    path('spotify/login/', views.SpotifyLoginView.as_view(), name='spotify-login'),
    path('spotify/logout/', views.SpotifyLogoutView.as_view(), name='spotify-logout'),
]
