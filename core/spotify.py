from django.conf import settings
import requests
import base64
import logging
from urllib.parse import quote, urlencode

logger = logging.getLogger(__name__)

class SpotifyClient:
    AUTH_URL = 'https://accounts.spotify.com/authorize'
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    API_BASE_URL = 'https://api.spotify.com/v1'
    
    SCOPES = [
        'user-read-private',
        'user-read-email',
        'playlist-read-private',
        'playlist-read-collaborative',
        'user-top-read',
        'user-read-recently-played',
        'user-library-read'
    ]

    @classmethod
    def get_auth_url(cls):
        """Generate OAuth URL for Spotify login."""
        try:
            auth_params = {
                'client_id': settings.SPOTIFY_CLIENT_ID,
                'response_type': 'code',
                'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
                'scope': settings.SPOTIFY_SCOPE,
                'show_dialog': True
            }
            # Construct URL for Spotify authorization
            auth_url = f"{cls.AUTH_URL}?{urlencode(auth_params)}"
            return auth_url
        except Exception as e:
            logger.error(f"Error generating Spotify auth URL: {str(e)}")
            raise

    @classmethod
    def get_client_credentials(cls):
        """
        Get client credentials access token for server-to-server API requests.
        This flow doesn't require user authorization and is suitable for
        accessing public data or data that doesn't require user permissions.
        """
        try:
            # Create authorization header
            auth_header = base64.b64encode(
                f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
            ).decode()

            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            data = {
                'grant_type': 'client_credentials'
            }

            logger.debug("Requesting client credentials token from Spotify")
            response = requests.post(cls.TOKEN_URL, headers=headers, data=data)
            response.raise_for_status()
            
            token_info = response.json()
            logger.debug("Successfully received client credentials token")
            return token_info['access_token']
            
        except Exception as e:
            logger.error(f"Error getting client credentials: {str(e)}")
            raise

    @classmethod
    def get_tokens(cls, auth_code):
        """Exchange authorization code for access and refresh tokens."""
        try:
            # Create authorization header
            auth_header = base64.b64encode(
                f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
            ).decode()

            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            # Prepare request data
            data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': settings.SPOTIFY_REDIRECT_URI
            }

            logger.debug("Requesting tokens from Spotify")
            response = requests.post(cls.TOKEN_URL, headers=headers, data=data)
            response.raise_for_status()
            
            tokens = response.json()
            logger.debug("Successfully received tokens from Spotify")
            return tokens

        except Exception as e:
            logger.error(f"Error getting Spotify tokens: {str(e)}")
            raise

    def __init__(self, access_token=None, refresh_token=None):
        """Initialize the client with optional access and refresh tokens."""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.session = requests.Session()
        if access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            })

    def get_user_profile(self):
        """Get the current user's Spotify profile."""
        try:
            logger.debug("Fetching user profile from Spotify")
            response = self.session.get(f'{self.API_BASE_URL}/me')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise

    def get_user_playlists(self, limit=50, offset=0):
        """Get the current user's playlists."""
        try:
            logger.debug(f"Fetching user playlists (limit={limit}, offset={offset})")
            response = self.session.get(
                f'{self.API_BASE_URL}/me/playlists',
                params={'limit': limit, 'offset': offset}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting user playlists: {str(e)}")
            raise

    def get_recently_played(self, limit=20):
        """Get user's recently played tracks."""
        try:
            logger.debug(f"Fetching recently played tracks (limit={limit})")
            response = self.session.get(
                f'{self.API_BASE_URL}/me/player/recently-played',
                params={'limit': limit}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting recently played tracks: {str(e)}")
            raise

    def get_user_top_artists(self, limit=20, offset=0, time_range='medium_term'):
        """Get user's top artists."""
        try:
            logger.debug(f"Fetching top artists (limit={limit}, offset={offset}, time_range={time_range})")
            response = self.session.get(
                f'{self.API_BASE_URL}/me/top/artists',
                params={
                    'limit': limit,
                    'offset': offset,
                    'time_range': time_range
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting top artists: {str(e)}")
            raise

    def get_playlist(self, playlist_id):
        """Get a playlist by ID."""
        try:
            logger.debug(f"Fetching playlist {playlist_id}")
            response = self.session.get(f'{self.API_BASE_URL}/playlists/{playlist_id}')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting playlist: {str(e)}")
            raise

    def get_artist(self, artist_id):
        """Get an artist by ID."""
        try:
            logger.debug(f"Fetching artist {artist_id}")
            response = self.session.get(f'{self.API_BASE_URL}/artists/{artist_id}')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting artist: {str(e)}")
            raise

    def _handle_auth_error(self, response):
        """Handle 401 Unauthorized responses by refreshing the access token."""
        if response.status_code == 401:
            try:
                self.refresh_token()
                return True
            except Exception as e:
                logger.error(f"Error refreshing token: {str(e)}")
                return False
        return False

    def get_tracks_features(self, track_ids):
        """Get audio features for multiple tracks."""
        try:
            if not track_ids:
                return {'audio_features': []}
            
            logger.debug(f"Fetching audio features for {len(track_ids)} tracks")
            
            # Split track IDs into chunks of 100 (Spotify API limit)
            chunk_size = 100
            audio_features = []
            
            for i in range(0, len(track_ids), chunk_size):
                chunk = track_ids[i:i + chunk_size]
                max_retries = 2
                retry_count = 0
                
                while retry_count < max_retries:
                    try:
                        response = self.session.get(
                            f'{self.API_BASE_URL}/audio-features',
                            params={'ids': ','.join(chunk)}
                        )
                        
                        # Handle auth errors
                        if response.status_code in (401, 403):
                            logger.debug(f"Received {response.status_code}, attempting token refresh")
                            # Call the refresh_token method, not treating it as an attribute
                            new_token_data = self.refresh_token()
                            if new_token_data:
                                # Retry with new token
                                retry_count += 1
                                continue
                            else:
                                raise Exception("Token refresh failed")
                        
                        response.raise_for_status()
                        chunk_features = response.json()
                        
                        # Handle both response formats
                        features = chunk_features.get('audio_features', chunk_features)
                        valid_features = [f for f in features if f is not None]
                        audio_features.extend(valid_features)
                        break  # Success, exit retry loop
                        
                    except Exception as e:
                        retry_count += 1
                        if retry_count >= max_retries:
                            logger.error(f"Error getting features for chunk {i}-{i+chunk_size} after {max_retries} retries: {str(e)}")
                            # Add empty placeholders for failed chunks
                            audio_features.extend([None] * len(chunk))
                        else:
                            logger.warning(f"Retry {retry_count}/{max_retries} for chunk {i}-{i+chunk_size}: {str(e)}")
                            continue

            return {'audio_features': audio_features}
            
        except Exception as e:
            logger.error(f"Error getting track features: {str(e)}")
            return {'audio_features': []}
    def get_recommendations(self, seed_artists=None, seed_genres=None, seed_tracks=None, limit=20, **kwargs):
        """Get track recommendations based on seeds and parameters."""
        try:
            params = {'limit': limit}
            
            if (seed_artists):
                params['seed_artists'] = ','.join(seed_artists[:5])
            if (seed_genres):
                params['seed_genres'] = ','.join(seed_genres[:5])
            if (seed_tracks):
                params['seed_tracks'] = ','.join(seed_tracks[:5])
                
            # Add any additional parameters
            params.update(kwargs)
            
            logger.debug(f"Fetching recommendations with parameters: {params}")
            response = self.session.get(f'{self.API_BASE_URL}/recommendations', params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            raise
            
    def get_new_releases(self, limit=20, offset=0, country=None):
        """Get new album releases featured in Spotify."""
        try:
            params = {'limit': limit, 'offset': offset}
            if country:
                params['country'] = country
                
            logger.debug(f"Fetching new releases with parameters: {params}")
            response = self.session.get(f'{self.API_BASE_URL}/browse/new-releases', params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting new releases: {str(e)}")
            raise

    def get_featured_playlists(self, limit=20, offset=0, country=None, locale=None, timestamp=None):
        """Get Spotify featured playlists."""
        try:
            params = {'limit': limit, 'offset': offset}
            if country:
                params['country'] = country
            if locale:
                params['locale'] = locale
            if timestamp:
                params['timestamp'] = timestamp
                
            logger.debug(f"Fetching featured playlists with parameters: {params}")
            response = self.session.get(f'{self.API_BASE_URL}/browse/featured-playlists', params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting featured playlists: {str(e)}")
            raise
            
    def make_request(self, url, params=None):
        """Make a generic request to the given URL using the session's auth token."""
        try:
            response = self.session.get(url, params=params)
            if response.status_code == 403:
                # Try to refresh the token if we have one
                if hasattr(self, 'refresh_token'):
                    logger.debug("Got 403, attempting to refresh token")
                    new_tokens = self.refresh_token(self.refresh_token)
                    self.access_token = new_tokens['access_token']
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                    # Retry the request
                    response = self.session.get(url, params=params)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            raise

    def refresh_token(self):
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            logger.error("No refresh token available for token refresh")
            raise ValueError("No refresh token available")
            
        try:
            logger.debug("Attempting to refresh access token")
            # Create authorization header for client credentials
            auth_header = base64.b64encode(
                f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Prepare request data
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            
            response = requests.post(self.TOKEN_URL, headers=headers, data=data)
            
            if response.status_code != 200:
                logger.error(f"Token refresh failed with status {response.status_code}: {response.text}")
                raise Exception(f"Failed to refresh token: {response.text}")
                
            data = response.json()
            self.access_token = data['access_token']
            
            # Update the session headers with new token
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            
            # Store new refresh token if provided
            if 'refresh_token' in data:
                self.refresh_token = data['refresh_token']
                
            logger.info("Successfully refreshed access token")
            return data
            
        except Exception as e:
            logger.error(f"Error during token refresh: {str(e)}")
            raise