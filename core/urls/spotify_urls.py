from django.urls import path
from .. import views

app_name = 'core'  # Set app_name to match the main app namespace

urlpatterns = [
    # Spotify auth endpoints
    path('callback/', views.SpotifyCallbackView.as_view(), name='spotify-callback'),
    path('login/', views.SpotifyLoginView.as_view(), name='spotify-login'),
    path('logout/', views.SpotifyLogoutView.as_view(), name='spotify-logout'),
]
