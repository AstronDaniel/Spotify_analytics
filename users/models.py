from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import datetime

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
