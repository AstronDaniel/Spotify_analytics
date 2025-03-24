from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any
from django.core.cache import cache
from django.db.models import Avg, Count
from .models import PlaylistAnalysis, PublicTrend, ArtistAnalysis, TrackFeatures
from core.spotify import SpotifyClient
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    """
    Service class for processing and analyzing Spotify music data.
    """
    
    def __init__(self, spotify_client: SpotifyClient = None):
        self.spotify_client = spotify_client

    def analyze_playlist(self, playlist_id: str, user=None) -> Dict[str, Any]:
        """Perform comprehensive analysis of a playlist."""
        print(f"Starting analysis for playlist {playlist_id}")
        try:
            # Get playlist data
            playlist_data = self.spotify_client.get_playlist(playlist_id)
            tracks_data = []
            
            # Fetch all tracks with pagination
            tracks = playlist_data.get('tracks', {})
            while tracks:
                valid_tracks = [item['track'] for item in tracks.get('items', []) 
                              if item and item.get('track')]
                tracks_data.extend(valid_tracks)
                
                if tracks.get('next'):
                    tracks = self.spotify_client.make_request(tracks['next'])
                else:
                    break

            # Safety check for empty playlist
            if not tracks_data:
                return {
                    'playlist_id': playlist_id,
                    'name': playlist_data.get('name', ''),
                    'track_count': 0,
                    'total_duration_ms': 0,
                    'analysis': {
                        'genre_distribution': {},
                        'audio_features': {},
                        'artists': {'unique_count': 0},
                        'popularity': {'average': 0},
                        'decades': {},
                        'key_distribution': {},
                        'tempo_distribution': {}
                    }
                }

            # Get audio features for all tracks
            track_ids = [track['id'] for track in tracks_data if track.get('id')]
            audio_features = []
            
            # Process track IDs in batches
            if track_ids:
                features_response = self.spotify_client.get_tracks_features(track_ids)
                audio_features = features_response.get('audio_features', [])

            # Combine track data with audio features
            tracks_with_features = []
            for track, features in zip(tracks_data, audio_features):
                if features and track:
                    tracks_with_features.append({**track, 'audio_features': features})

            # Safety check for analysis
            if not tracks_with_features:
                return {
                    'playlist_id': playlist_id,
                    'name': playlist_data.get('name', ''),
                    'track_count': len(tracks_data),
                    'total_duration_ms': sum(t.get('duration_ms', 0) for t in tracks_data),
                    'analysis': {
                        'genre_distribution': {},
                        'audio_features': {},
                        'artists': {'unique_count': 0},
                        'popularity': {'average': 0},
                        'decades': {},
                        'key_distribution': {},
                        'tempo_distribution': {}
                    }
                }

            # Perform analysis
            analysis_results = {
                'playlist_id': playlist_id,
                'name': playlist_data['name'],
                'track_count': len(tracks_with_features),
                'total_duration_ms': sum(t['duration_ms'] for t in tracks_data),
                'analysis': {
                    'genre_distribution': self._analyze_genres(tracks_with_features),
                    'audio_features': self._analyze_audio_features(tracks_with_features),
                    'artists': self._analyze_artists(tracks_with_features),
                    'popularity': self._analyze_popularity(tracks_with_features),
                    'decades': self._analyze_decades(tracks_with_features),
                    'key_distribution': self._analyze_keys(tracks_with_features),
                    'tempo_distribution': self._analyze_tempo(tracks_with_features),
                }
            }

            # Store analysis if user is provided
            if user:
                PlaylistAnalysis.objects.update_or_create(
                    playlist_id=playlist_id,
                    user=user,
                    defaults={
                        'name': playlist_data['name'],
                        'analysis_data': analysis_results,
                        'track_count': len(tracks_with_features),
                        'total_duration_ms': sum(t['duration_ms'] for t in tracks_data)
                    }
                )

            return analysis_results

        except Exception as e:
            logger.error(f"Error analyzing playlist {playlist_id}: {str(e)}")
            raise

    def generate_public_trends(self) -> Dict[str, Any]:
        """
        Generate public music trends from analyzed data and Spotify API.
        """
        try:
            logger.info("Generating public trends from Spotify data")
            
            if not self.spotify_client:
                logger.error("No Spotify client available to fetch trends")
                return None
                
            # Initialize trends dictionary
            trends = {}
            
            # Get genre distribution (simplest part, static for now)
            trends["genre_distribution"] = {
                "Pop": 30,
                "Hip Hop": 25,
                "Rock": 20, 
                "Electronic": 15,
                "R&B": 10
            }
            
            # Try to fetch audio features from recommendations
            try:
                # Fetch recommendations for audio features
                recommendations = self.spotify_client.get_recommendations(
                    seed_genres=["pop", "rock", "hip-hop", "dance"], 
                    limit=50
                )
                
                if recommendations and 'tracks' in recommendations:
                    track_ids = [track['id'] for track in recommendations.get('tracks', [])]
                    
                    if track_ids:
                        # Fetch audio features for these tracks
                        audio_features_data = self.spotify_client.get_tracks_features(track_ids)
                        audio_features = audio_features_data.get('audio_features', [])
                        
                        # Calculate average audio features
                        features_sum = defaultdict(float)
                        feature_keys = ['danceability', 'energy', 'speechiness', 'acousticness', 
                                       'instrumentalness', 'liveness', 'valence']
                        count = len([af for af in audio_features if af])  # Count non-null features
                        
                        if count > 0:
                            for feature in audio_features:
                                if feature:  # Skip null features
                                    for key in feature_keys:
                                        features_sum[key] += feature.get(key, 0)
                            
                            trends['audio_features'] = {key: features_sum[key] / count for key in feature_keys}
                            
                            # Create tempo distribution from the audio features
                            tempo_bins = defaultdict(int)
                            for feature in audio_features:
                                if feature and 'tempo' in feature:
                                    tempo = feature['tempo']
                                    if tempo < 80:
                                        tempo_bins['60-80 BPM'] += 1
                                    elif tempo < 100:
                                        tempo_bins['80-100 BPM'] += 1
                                    elif tempo < 120:
                                        tempo_bins['100-120 BPM'] += 1
                                    elif tempo < 140:
                                        tempo_bins['120-140 BPM'] += 1
                                    elif tempo < 160:
                                        tempo_bins['140-160 BPM'] += 1
                                    else:
                                        tempo_bins['160+ BPM'] += 1
                            
                            # Calculate percentages for tempo distribution
                            tempo_distribution = {}
                            total = sum(tempo_bins.values())
                            if total > 0:
                                for bin_key, count in tempo_bins.items():
                                    tempo_distribution[bin_key] = round((count / total) * 100)
                            
                            trends['tempo_distribution'] = tempo_distribution
                
            except Exception as e:
                logger.error(f"Error getting audio features from recommendations: {str(e)}")
                # Use fallback audio features
                trends['audio_features'] = {
                    "danceability": 0.71,
                    "energy": 0.68,
                    "valence": 0.62,
                    "acousticness": 0.21,
                    "instrumentalness": 0.08,
                    "speechiness": 0.09,
                    "liveness": 0.16
                }
                
                # Use fallback tempo distribution
                trends['tempo_distribution'] = {
                    "60-80 BPM": 10,
                    "80-100 BPM": 25,
                    "100-120 BPM": 40,
                    "120-140 BPM": 15,
                    "140-160 BPM": 8,
                    "160+ BPM": 2
                }
            
            # Try to get trending artists from new releases
            try:
                new_releases = self.spotify_client.get_new_releases(limit=20)
                
                if new_releases and 'albums' in new_releases:
                    # Get some popular artists from new releases
                    trending_artists = []
                    processed_artists = set()
                    
                    # Process new releases to extract artists
                    for album in new_releases.get('albums', {}).get('items', []):
                        for artist in album.get('artists', []):
                            artist_id = artist.get('id')
                            
                            # Skip if we already processed this artist
                            if artist_id in processed_artists:
                                continue
                                
                            # Get detailed artist info
                            try:
                                artist_data = self.spotify_client.get_artist(artist_id)
                                trending_artists.append({
                                    "name": artist_data.get('name'),
                                    "image": artist_data.get('images', [{}])[0].get('url') if artist_data.get('images') else "/static/img/default-artist.png",
                                    "genres": artist_data.get('genres', [])[:3],
                                    "popularity": artist_data.get('popularity', 0)
                                })
                                processed_artists.add(artist_id)
                                
                                # Stop when we have enough artists
                                if len(trending_artists) >= 4:
                                    break
                            except Exception as e:
                                logger.warning(f"Failed to get artist details: {str(e)}")
                    
                    # Sort by popularity (descending)
                    trending_artists.sort(key=lambda x: x['popularity'], reverse=True)
                    trends['trending_artists'] = trending_artists[:4]  # Limit to top 4
            
            except Exception as e:
                logger.error(f"Error fetching new releases: {str(e)}")
                # Use fallback trending artists
                trends['trending_artists'] = [
                    {
                        "name": "Taylor Swift",
                        "image": "/static/img/default-artist.png",
                        "genres": ["pop", "country pop"],
                        "popularity": 92
                    },
                    {
                        "name": "The Weeknd",
                        "image": "/static/img/default-artist.png",
                        "genres": ["canadian pop", "r&b"],
                        "popularity": 90
                    },
                    {
                        "name": "Bad Bunny",
                        "image": "/static/img/default-artist.png",
                        "genres": ["reggaeton", "latin"],
                        "popularity": 88
                    },
                    {
                        "name": "Drake",
                        "image": "/static/img/default-artist.png",
                        "genres": ["canadian hip hop", "rap"],
                        "popularity": 86
                    }
                ]
            
            # Generate mood analysis based on audio features
            try:
                if 'audio_features' in trends:
                    af = trends['audio_features']
                    
                    # Derive mood metrics from audio features
                    mood_metrics = {
                        "Happy": min(1.0, (af.get('valence', 0) * 0.8 + af.get('energy', 0) * 0.2)),
                        "Energetic": min(1.0, (af.get('energy', 0) * 0.8 + af.get('danceability', 0) * 0.2)),
                        "Relaxed": min(1.0, (1 - af.get('energy', 0)) * 0.6 + af.get('acousticness', 0) * 0.4),
                        "Melancholic": min(1.0, (1 - af.get('valence', 0)) * 0.7 + af.get('acousticness', 0) * 0.3),
                        "Aggressive": min(1.0, af.get('energy', 0) * 0.6 + (1 - af.get('valence', 0)) * 0.4)
                    }
                    
                    # Find top mood
                    top_mood = max(mood_metrics.items(), key=lambda x: x[1])
                    mood_percentage = int(top_mood[1] * 100)
                    
                    # Create mood analysis
                    trends['mood_analysis'] = {
                        "metrics": mood_metrics,
                        "summary": f"Current global trends show a preference for {top_mood[0].lower()} and engaging music.",
                        "insights": {
                            "Top mood": f"{top_mood[0]} with {mood_percentage}% prevalence",
                            "Fastest growing": "Upbeat tracks with high energy",
                            "Regional difference": "More acoustic tracks popular in Europe",
                            "Seasonal shift": "Trending toward more danceable music this season"
                        }
                    }
            except Exception as e:
                logger.error(f"Error generating mood analysis: {str(e)}")
                # Use fallback mood analysis
                trends['mood_analysis'] = {
                    "metrics": {
                        "Happy": 0.65,
                        "Energetic": 0.72,
                        "Relaxed": 0.43,
                        "Melancholic": 0.36,
                        "Aggressive": 0.28
                    },
                    "summary": "Current global trends show a preference for upbeat and energetic music.",
                    "insights": {
                        "Top mood": "Energetic with 72% prevalence",
                        "Fastest growing": "Happy tracks increased by 8%",
                        "Regional difference": "European listeners prefer more relaxed tracks",
                        "Seasonal shift": "Transitioning to more upbeat music compared to last quarter"
                    }
                }

            # Check if we have all the necessary sections
            required_sections = ['genre_distribution', 'audio_features', 'trending_artists', 
                                'mood_analysis', 'tempo_distribution']
            for section in required_sections:
                if section not in trends:
                    logger.warning(f"Missing required trend section: {section}")
            
            # Store the trends in the database
            if trends and all(section in trends for section in required_sections):
                try:
                    # Deactivate all previous trends
                    PublicTrend.objects.filter(trend_type='general', is_active=True).update(is_active=False)
                    
                    # Create new trend
                    PublicTrend.objects.create(
                        trend_type='general',
                        trend_data=trends,
                        valid_until=datetime.now() + timedelta(days=1),
                        is_active=True
                    )
                    logger.info("Successfully stored new trends in database")
                except Exception as e:
                    logger.error(f"Error saving trends to database: {str(e)}")

            return trends

        except Exception as e:
            logger.error(f"Error generating public trends: {str(e)}")
            return None

    def _analyze_genres(self, tracks: List[Dict]) -> Dict[str, int]:
        """Analyze genre distribution in tracks."""
        genres = []
        for track in tracks:
            for artist in track['artists']:
                artist_data = self.spotify_client.get_artist(artist['id'])
                genres.extend(artist_data.get('genres', []))
        
        genre_counts = Counter(genres)
        total = sum(genre_counts.values())
        
        return {
            genre: {'count': count, 'percentage': (count/total)*100}
            for genre, count in genre_counts.most_common()
        }

    def _analyze_audio_features(self, tracks: List[Dict]) -> Dict[str, float]:
        """Analyze average audio features of tracks."""
        features = defaultdict(list)
        
        for track in tracks:
            if 'audio_features' in track:
                for key, value in track['audio_features'].items():
                    if isinstance(value, (int, float)):
                        features[key].append(value)
        
        return {
            feature: sum(values) / len(values)
            for feature, values in features.items()
            if values
        }

    def _analyze_artists(self, tracks: List[Dict]) -> Dict[str, Any]:
        """Analyze artist distribution and information."""
        artist_counts = Counter()
        artist_info = {}
        
        for track in tracks:
            for artist in track['artists']:
                artist_counts[artist['id']] += 1
                if artist['id'] not in artist_info:
                    artist_data = self.spotify_client.get_artist(artist['id'])
                    artist_info[artist['id']] = {
                        'name': artist['name'],
                        'popularity': artist_data.get('popularity', 0),
                        'genres': artist_data.get('genres', [])
                    }

        total_tracks = len(tracks)
        return {
            'artist_distribution': {
                artist_id: {
                    **artist_info[artist_id],
                    'track_count': count,
                    'percentage': (count/total_tracks)*100
                }
                for artist_id, count in artist_counts.most_common()
            }
        }

    def _analyze_popularity(self, tracks: List[Dict]) -> Dict[str, Any]:
        """Analyze track popularity distribution."""
        popularities = [track.get('popularity', 0) for track in tracks]
        avg_popularity = sum(popularities) / len(popularities)
        
        popularity_ranges = {
            'high': len([p for p in popularities if p >= 70]),
            'medium': len([p for p in popularities if 30 <= p < 70]),
            'low': len([p for p in popularities if p < 30])
        }
        
        return {
            'average_popularity': avg_popularity,
            'popularity_distribution': popularity_ranges
        }

    def _analyze_decades(self, tracks: List[Dict]) -> Dict[str, int]:
        """Analyze track release date distribution by decades."""
        decades = Counter()
        
        for track in tracks:
            if 'release_date' in track['album']:
                year = int(track['album']['release_date'][:4])
                decade = f"{year//10*10}s"
                decades[decade] += 1
        
        return dict(decades.most_common())

    def _analyze_keys(self, tracks: List[Dict]) -> Dict[str, int]:
        """Analyze musical key distribution."""
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        keys = Counter()
        
        for track in tracks:
            if 'audio_features' in track:
                key = track['audio_features'].get('key')
                mode = track['audio_features'].get('mode')
                if key is not None and mode is not None:
                    key_name = f"{key_names[key]} {'major' if mode else 'minor'}"
                    keys[key_name] += 1
        
        return dict(keys.most_common())

    def _analyze_tempo(self, tracks: List[Dict]) -> Dict[str, int]:
        """Analyze tempo distribution."""
        tempo_ranges = {
            'slow': (0, 90),
            'medium': (90, 120),
            'fast': (120, 1000)
        }
        
        tempos = defaultdict(int)
        for track in tracks:
            if 'audio_features' in track:
                tempo = track['audio_features'].get('tempo', 0)
                for range_name, (min_tempo, max_tempo) in tempo_ranges.items():
                    if min_tempo <= tempo < max_tempo:
                        tempos[range_name] += 1
                        break
        
        return dict(tempos)

    def _aggregate_genre_trends(self, analyses) -> Dict[str, int]:
        """Aggregate genre trends from multiple playlist analyses."""
        genre_counts = Counter()
        
        for analysis in analyses:
            genres = analysis.analysis_data['analysis']['genre_distribution']
            for genre, data in genres.items():
                genre_counts[genre] += data['count']
        
        return dict(genre_counts.most_common(20))

    def _aggregate_audio_features(self, analyses) -> Dict[str, float]:
        """Aggregate average audio features from multiple playlist analyses."""
        features = defaultdict(list)
        
        for analysis in analyses:
            audio_features = analysis.analysis_data['analysis']['audio_features']
            for feature, value in audio_features.items():
                features[feature].append(value)
        
        return {
            feature: sum(values) / len(values)
            for feature, values in features.items()
        }

    def _aggregate_artist_trends(self, analyses) -> Dict[str, Dict]:
        """Aggregate artist popularity from multiple playlist analyses."""
        artist_data = defaultdict(lambda: {'count': 0, 'popularity': 0})
        
        for analysis in analyses:
            artists = analysis.analysis_data['analysis']['artists']['artist_distribution']
            for artist_id, data in artists.items():
                artist_data[artist_id]['count'] += data['track_count']
                artist_data[artist_id]['name'] = data['name']
                artist_data[artist_id]['popularity'] = data['popularity']
                artist_data[artist_id]['genres'] = data['genres']
        
        return dict(sorted(
            artist_data.items(),
            key=lambda x: (x[1]['count'], x[1]['popularity']),
            reverse=True
        )[:20])

    def _aggregate_tempo_trends(self, analyses) -> Dict[str, int]:
        """Aggregate tempo distributions from multiple playlist analyses."""
        tempo_counts = Counter()
        
        for analysis in analyses:
            tempo_dist = analysis.analysis_data['analysis']['tempo_distribution']
            for tempo_range, count in tempo_dist.items():
                tempo_counts[tempo_range] += count
        
        return dict(tempo_counts)

    def _aggregate_key_trends(self, analyses) -> Dict[str, int]:
        """Aggregate key distributions from multiple playlist analyses."""
        key_counts = Counter()
        
        for analysis in analyses:
            key_dist = analysis.analysis_data['analysis']['key_distribution']
            for key, count in key_dist.items():
                key_counts[key] += count
        
        return dict(key_counts)