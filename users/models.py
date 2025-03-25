from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import datetime
import time
import logging

logger = logging.getLogger(__name__)

class User(AbstractUser):
    """Custom user model with Spotify integration."""
    
    # Spotify-related fields
    spotify_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    spotify_access_token = models.TextField(blank=True, null=True)
    spotify_refresh_token = models.TextField(blank=True, null=True)
    spotify_token_expires_at = models.IntegerField(blank=True, null=True)
    spotify_profile_image = models.URLField(max_length=500, blank=True, null=True)
    spotify_last_sync = models.DateTimeField(blank=True, null=True)
    
    # User preferences
    is_public = models.BooleanField(default=False)
    dark_mode = models.BooleanField(default=False)
    
    @property
    def is_spotify_linked(self):
        """Check if user has linked their Spotify account."""
        return bool(self.spotify_access_token and self.spotify_refresh_token)

    @property
    def is_spotify_token_expired(self):
        """Check if Spotify access token is expired."""
        if not self.spotify_token_expires_at:
            return True
        
        # Convert token expiry from seconds to datetime
        expiry_time = timezone.now() + datetime.timedelta(seconds=self.spotify_token_expires_at)
        return timezone.now() >= expiry_time

    def refresh_spotify_token(self):
        """Refresh the Spotify access token if it's expired."""
        if not self.is_spotify_linked:
            return False
            
        # Only refresh if token is expired or about to expire
        current_time = int(time.time())
        if self.spotify_token_expires_at and current_time < self.spotify_token_expires_at - 60:
            return True  # Token is still valid
            
        try:
            from core.spotify import SpotifyClient
            spotify = SpotifyClient(
                access_token=self.spotify_access_token,
                refresh_token=self.spotify_refresh_token
            )
            token_data = spotify.refresh_auth_token()  # Using the new method name
            
            # Update tokens
            self.spotify_access_token = token_data['access_token']
            if 'refresh_token' in token_data:
                self.spotify_refresh_token = token_data['refresh_token']
            self.spotify_token_expires_at = int(time.time()) + token_data['expires_in']
            self.save()
            
            return True
        except Exception as e:
            logger.error(f"Failed to refresh Spotify token: {str(e)}")
            return False

    def spotify_disconnect(self):
        """Remove Spotify connection."""
        self.spotify_id = None
        self.spotify_access_token = None
        self.spotify_refresh_token = None
        self.spotify_token_expires_at = None
        self.spotify_profile_image = None
        self.spotify_last_sync = None
        self.save()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
