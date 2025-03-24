from rest_framework import serializers
from users.models import User
from analytics.models import (
    AnalyticsHistory,
    PlaylistAnalysis,
    PublicTrend,
    ArtistAnalysis,
    TrackFeatures
)

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'spotify_id', 'is_public']
        read_only_fields = ['id', 'spotify_id']

class AnalyticsHistorySerializer(serializers.ModelSerializer):
    """Serializer for AnalyticsHistory model."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = AnalyticsHistory
        fields = ['id', 'user', 'analysis_type', 'result_data', 'is_public', 'created_at']
        read_only_fields = ['id', 'created_at']

class PlaylistAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for PlaylistAnalysis model."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = PlaylistAnalysis
        fields = [
            'id', 'playlist_id', 'user', 'name', 'is_public',
            'analysis_data', 'track_count', 'total_duration_ms',
            'last_updated', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'last_updated', 'created_at']

class PublicTrendSerializer(serializers.ModelSerializer):
    """Serializer for PublicTrend model."""
    class Meta:
        model = PublicTrend
        fields = [
            'id', 'trend_type', 'trend_data', 'created_at',
            'valid_until', 'is_active'
        ]
        read_only_fields = ['id', 'created_at']

class ArtistAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for ArtistAnalysis model."""
    class Meta:
        model = ArtistAnalysis
        fields = [
            'id', 'artist_id', 'name', 'analysis_data', 'popularity',
            'genres', 'last_updated', 'created_at'
        ]
        read_only_fields = ['id', 'last_updated', 'created_at']

class TrackFeaturesSerializer(serializers.ModelSerializer):
    """Serializer for TrackFeatures model."""
    class Meta:
        model = TrackFeatures
        fields = [
            'id', 'track_id', 'name', 'artist_name', 'danceability',
            'energy', 'key', 'loudness', 'mode', 'speechiness',
            'acousticness', 'instrumentalness', 'liveness', 'valence',
            'tempo', 'duration_ms', 'time_signature', 'last_updated',
            'created_at'
        ]
        read_only_fields = ['id', 'last_updated', 'created_at']

class TrendDataSerializer(serializers.Serializer):
    """Serializer for trend data response."""
    genre_distribution = serializers.DictField(
        child=serializers.IntegerField(min_value=0, max_value=100)
    )
    audio_features = serializers.DictField(
        child=serializers.FloatField(min_value=0, max_value=1)
    )
    trending_artists = serializers.ListField(
        child=serializers.DictField()
    )
    mood_analysis = serializers.DictField()
    tempo_distribution = serializers.DictField(
        child=serializers.IntegerField(min_value=0)
    )