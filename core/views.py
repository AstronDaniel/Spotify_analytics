from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect, render
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseBadRequest, JsonResponse
import logging
import time
from .spotify import SpotifyClient
from analytics.services import AnalyticsService

logger = logging.getLogger(__name__)

class HomeView(TemplateView):
    template_name = 'core/home.html'

class AboutView(TemplateView):
    template_name = 'core/about.html'

class TrendsView(TemplateView):
    template_name = 'core/trends.html'

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'
    login_url = 'core:spotify-login'

class PlaylistsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/playlists.html'
    login_url = 'core:spotify-login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            if not self.request.user.is_spotify_linked:
                context['playlists'] = []
                return context
                
            # Initialize SpotifyClient with the user's access token
            spotify_client = SpotifyClient(self.request.user.spotify_access_token)
            
            # Fetch user's playlists
            playlists_data = spotify_client.get_user_playlists(limit=50)
            
            # Get analyzed playlists for this user
            from analytics.models import PlaylistAnalysis
            analyzed_playlists = {
                p.playlist_id: p 
                for p in PlaylistAnalysis.objects.filter(user=self.request.user)
            }
            
            # Extract playlist info and add to context
            playlists = []
            for item in playlists_data.get('items', []):
                playlist_id = item.get('id')
                analysis = analyzed_playlists.get(playlist_id)
                
                playlist = {
                    'id': playlist_id,
                    'name': item.get('name'),
                    'tracks_total': item.get('tracks', {}).get('total', 0),
                    'image_url': item.get('images', [{}])[0].get('url') if item.get('images') else None,
                    'spotify_url': item.get('external_urls', {}).get('spotify'),
                    'is_analyzed': analysis is not None,
                    'total_duration_ms': analysis.total_duration_ms if analysis else 0,
                    'analysis_date': analysis.last_updated if analysis else None,
                    'top_genre': analysis.analysis_data.get('analysis', {}).get('genre_distribution', {}).get('dominant') if analysis else None,
                    'avg_popularity': analysis.analysis_data.get('analysis', {}).get('popularity', {}).get('average') if analysis else None,
                }
                playlists.append(playlist)
                
            context['playlists'] = playlists
            
        except Exception as e:
            logger.error(f"Error fetching playlists: {str(e)}")
            context['playlists'] = []
            messages.error(self.request, "Failed to load your playlists. Please try again.")
            
        return context

class PlaylistDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'core/playlist_detail.html'
    login_url = 'core:spotify-login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        playlist_id = kwargs.get('playlist_id')
        refresh = self.request.GET.get('refresh') == 'true'
        
        try:
            if not self.request.user.is_spotify_linked:
                messages.error(self.request, "Please connect your Spotify account first.")
                return redirect('core:spotify-login')
            
            # Initialize SpotifyClient with user's access token    
            spotify_client = SpotifyClient(self.request.user.spotify_access_token)
            
            # Get playlist details
            playlist_data = spotify_client.get_playlist(playlist_id)
            
            # Get playlist analysis from database if it exists and we're not refreshing
            from analytics.models import PlaylistAnalysis
            analysis = None if refresh else PlaylistAnalysis.objects.filter(
                playlist_id=playlist_id,
                user=self.request.user
            ).first()
            
            # If no analysis exists or we're refreshing, create one
            # If no analysis exists or we're refreshing, create one
            if not analysis:
                analytics_service = AnalyticsService(spotify_client=spotify_client)
                analysis_data = analytics_service.analyze_playlist(playlist_id, user=self.request.user)
                # Try to get the analysis after creation, handle if not found
                try:
                    analysis = PlaylistAnalysis.objects.get(playlist_id=playlist_id, user=self.request.user)
                except PlaylistAnalysis.DoesNotExist:
                    # Create the analysis if it doesn't exist
                    from analytics.models import PlaylistAnalysis
                    analysis = PlaylistAnalysis.objects.create(
                        playlist_id=playlist_id,
                        user=self.request.user,
                        analysis_data=analysis_data,
                        total_duration_ms=0  # Set a default or calculate this
                    )
            context.update({
                'playlist': {
                    'id': playlist_data['id'],
                    'name': playlist_data['name'],
                    'tracks_total': playlist_data['tracks']['total'],
                    'total_duration_ms': analysis.total_duration_ms,
                    'image_url': playlist_data['images'][0]['url'] if playlist_data.get('images') else None,
                    'spotify_url': playlist_data['external_urls']['spotify'],
                    'owner': self.request.user if playlist_data['owner']['id'] == self.request.user.spotify_id else None,
                    'is_public': analysis.is_public,
                },
                'analysis': analysis.analysis_data,
            })
            
        except Exception as e:
            logger.error(f"Error loading playlist detail: {str(e)}")
            messages.error(self.request, "Failed to load playlist analysis. Please try again.")
            context['playlist'] = None
            context['analysis'] = None
            
        return context

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'core/profile.html'
    login_url = 'core:spotify-login'

class SpotifyLoginView(RedirectView):
    """Handle Spotify login."""
    
    def get_redirect_url(self, *args, **kwargs):
        try:
            logger.info("Generating Spotify auth URL")
            auth_url = SpotifyClient.get_auth_url()
            logger.debug(f"Generated auth URL: {auth_url}")
            return auth_url
        except Exception as e:
            logger.error(f"Error during Spotify login: {str(e)}")
            messages.error(self.request, "Failed to connect to Spotify. Please try again.")
            return reverse('core:home')

class SpotifyCallbackView(RedirectView):
    """Handle Spotify OAuth callback."""
    
    def get_redirect_url(self, *args, **kwargs):
        error = self.request.GET.get('error')
        if error:
            logger.error(f"Spotify auth error: {error}")
            messages.error(self.request, f"Authentication failed: {error}")
            return reverse('core:home')

        code = self.request.GET.get('code')
        if not code:
            logger.error("No authorization code received")
            messages.error(self.request, "Authentication failed: No authorization code received")
            return reverse('core:home')

        try:
            logger.info("Processing Spotify callback")
            # Get tokens using the authorization code
            token_info = SpotifyClient.get_tokens(code)
            
            # Initialize Spotify client with access token
            spotify = SpotifyClient(token_info['access_token'])
            
            # Get user profile
            profile = spotify.get_user_profile()
            
            # If user is not authenticated, create or get user and log them in
            if not self.request.user.is_authenticated:
                User = get_user_model()
                user, created = User.objects.get_or_create(
                    spotify_id=profile['id'],
                    defaults={
                        'username': profile['id'],
                        'email': profile.get('email', ''),
                    }
                )
                login(self.request, user)
            else:
                user = self.request.user
            
            # Update user's Spotify information
            user.spotify_id = profile['id']
            user.spotify_access_token = token_info['access_token']
            user.spotify_refresh_token = token_info['refresh_token']
            
            # Store token expiration time as an absolute timestamp instead of relative seconds
            user.spotify_token_expires_at = int(time.time()) + token_info['expires_in']
            
            user.spotify_profile_image = profile.get('images', [{}])[0].get('url', '')
            user.save()

            messages.success(self.request, "Successfully connected to Spotify!")
            return reverse('core:dashboard')
            
        except Exception as e:
            logger.error(f"Error during Spotify callback: {str(e)}")
            messages.error(self.request, "Failed to complete authentication. Please try again.")
            return reverse('core:home')

class SpotifyLogoutView(LoginRequiredMixin, RedirectView):
    """Handle Spotify logout."""
    
    def get_redirect_url(self, *args, **kwargs):
        try:
            user = self.request.user
            user.spotify_access_token = None
            user.spotify_refresh_token = None
            user.spotify_token_expires_at = None
            user.save()
            
            messages.success(self.request, "Successfully disconnected from Spotify.")
        except Exception as e:
            logger.error(f"Error during Spotify logout: {str(e)}")
            messages.error(self.request, "Error disconnecting from Spotify.")
            
        return reverse('core:home')

# Error handlers
def page_not_found(request, exception):
    return render(request, '404.html', status=404)

def server_error(request):
    return render(request, '500.html', status=500)

def service_unavailable(request, exception=None):
    return render(request, 'offline.html', status=503)

# AJAX endpoints
def check_spotify_connection(request):
    """Check if user's Spotify connection is valid."""
    if not request.user.is_authenticated:
        return JsonResponse({'connected': False, 'error': 'Not authenticated'})
    
    try:
        spotify = SpotifyClient(request.user.spotify_access_token)
        profile = spotify.get_user_profile()
        return JsonResponse({'connected': True})
    except Exception as e:
        logger.error(f"Error checking Spotify connection: {str(e)}")
        return JsonResponse({'connected': False, 'error': str(e)})
