from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User

class AnalyticsHistory(models.Model):
    """
    Stores user-specific analytics results and history.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    analysis_type = models.CharField(max_length=50)
    result_data = models.JSONField()
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('analytics history')
        verbose_name_plural = _('analytics histories')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.analysis_type} - {self.created_at}"

class PlaylistAnalysis(models.Model):
    """
    Stores analysis results for specific playlists.
    """
    playlist_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_public = models.BooleanField(default=False)
    analysis_data = models.JSONField()
    track_count = models.IntegerField(default=0)
    total_duration_ms = models.BigIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('playlist analysis')
        verbose_name_plural = _('playlist analyses')
        ordering = ['-last_updated']
        unique_together = ['playlist_id', 'user']

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class PublicTrend(models.Model):
    """
    Stores public music trends and statistics.
    """
    TREND_TYPES = [
        ('genre', 'Genre Distribution'),
        ('artist', 'Artist Popularity'),
        ('feature', 'Audio Features'),
        ('tempo', 'Tempo Distribution'),
        ('key', 'Key Distribution'),
        ('general', 'General Trends'),
    ]

    trend_type = models.CharField(max_length=50, choices=TREND_TYPES)
    trend_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('public trend')
        verbose_name_plural = _('public trends')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_trend_type_display()} - {self.created_at}"

class ArtistAnalysis(models.Model):
    """
    Stores analysis results for artists.
    """
    artist_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    analysis_data = models.JSONField()
    popularity = models.IntegerField()
    genres = models.JSONField()
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('artist analysis')
        verbose_name_plural = _('artist analyses')
        ordering = ['-popularity']

    def __str__(self):
        return f"{self.name} - Popularity: {self.popularity}"

class TrackFeatures(models.Model):
    """
    Stores audio features for tracks.
    """
    track_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    danceability = models.FloatField()
    energy = models.FloatField()
    key = models.IntegerField()
    loudness = models.FloatField()
    mode = models.IntegerField()
    speechiness = models.FloatField()
    acousticness = models.FloatField()
    instrumentalness = models.FloatField()
    liveness = models.FloatField()
    valence = models.FloatField()
    tempo = models.FloatField()
    duration_ms = models.IntegerField()
    time_signature = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('track features')
        verbose_name_plural = _('track features')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.artist_name}"
