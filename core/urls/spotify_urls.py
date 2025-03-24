from django.urls import path
from .. import views

# No app_name here to avoid namespace conflicts
urlpatterns = [
    # Spotify auth endpoints
    path('callback/', views.SpotifyCallbackView.as_view(), name='spotify-callback'),
    path('login/', views.SpotifyLoginView.as_view(), name='spotify-login'),
    path('logout/', views.SpotifyLogoutView.as_view(), name='spotify-logout'),
]
