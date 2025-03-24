from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Core API endpoints
    path('trends/', views.TrendsView.as_view(), name='trends'),
    path('user/analytics/', views.UserAnalyticsView.as_view(), name='user-analytics'),
    path('playlists/<str:playlist_id>/refresh/', views.PlaylistAnalysisRefreshView.as_view(), name='playlist-refresh'),
]