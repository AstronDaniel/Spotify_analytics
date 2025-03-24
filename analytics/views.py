from django.shortcuts import render
from django.views.generic import DetailView
from .models import PlaylistAnalysis
from core.spotify import SpotifyClient

class PlaylistDetailView(DetailView):
    model = PlaylistAnalysis
    template_name = 'core/playlist_detail.html'
    context_object_name = 'analysis'
    
    def get_object(self, queryset=None):
        playlist_id = self.kwargs.get('playlist_id')
        try:
            return PlaylistAnalysis.objects.get(
                playlist_id=playlist_id,
                user=self.request.user
            )
        except PlaylistAnalysis.DoesNotExist:
            # Create a new analysis if it doesn't exist
            spotify = SpotifyClient(
                access_token=self.request.user.spotify_token,
                refresh_token=self.request.user.spotify_refresh_token
            )
            playlist_data = spotify.get_playlist(playlist_id)
            
            # Create new analysis
            analysis = PlaylistAnalysis.objects.create(
                playlist_id=playlist_id,
                user=self.request.user,
                name=playlist_data.get('name', ''),
                total_tracks=len(playlist_data.get('tracks', {}).get('items', []))
            )
            return analysis
