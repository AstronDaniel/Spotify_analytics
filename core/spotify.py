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
            # Print debug information about Spotify app configuration
            print(f"\n[DEBUG] Spotify Auth Configuration:")
            print(f"[DEBUG] Client ID: {settings.SPOTIFY_CLIENT_ID[:5]}...{settings.SPOTIFY_CLIENT_ID[-5:] if settings.SPOTIFY_CLIENT_ID else 'Not Set'}")
            print(f"[DEBUG] Redirect URI: {settings.SPOTIFY_REDIRECT_URI}")
            print(f"[DEBUG] Scopes: {settings.SPOTIFY_SCOPE}")
            
            auth_params = {
                'client_id': settings.SPOTIFY_CLIENT_ID,
                'response_type': 'code',
                'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
                'scope': settings.SPOTIFY_SCOPE,
                'show_dialog': True  # Always show the authorization dialog to allow different users to log in
            }
            # Construct URL for Spotify authorization
            auth_url = f"{cls.AUTH_URL}?{urlencode(auth_params)}"
            logger.info(f"Generated Spotify auth URL with scopes: {settings.SPOTIFY_SCOPE}")
            return auth_url
        except Exception as e:
            logger.error(f"Error generating Spotify auth URL: {str(e)}")
            print(f"\n[ERROR] Failed to generate Spotify auth URL: {str(e)}")
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
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                logger.error(f"Spotify API Error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code == 403:
                    raise PermissionError("Insufficient Spotify API permissions or unauthorized user")
                raise
            
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

            print(f"\n[DEBUG] Exchanging auth code for tokens")
            print(f"[DEBUG] Auth code length: {len(auth_code)}")
            print(f"[DEBUG] Redirect URI: {settings.SPOTIFY_REDIRECT_URI}")
            
            logger.debug("Requesting tokens from Spotify")
            response = requests.post(cls.TOKEN_URL, headers=headers, data=data)
            
            print(f"[DEBUG] Token response status: {response.status_code}")
            
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                error_details = e.response.json() if e.response.content else {}
                logger.error(f"Spotify API Error: {e.response.status_code} - {e.response.text}")
                print(f"\n[ERROR] Spotify API Error: {e.response.status_code}")
                print(f"[ERROR] Error details: {error_details}")
                
                if e.response.status_code == 403:
                    print(f"[ERROR] Permission denied. This could be due to:")
                    print(f"  - App in development mode (only authorized users can connect)")
                    print(f"  - Missing required scopes")
                    print(f"  - Invalid redirect URI")
                    raise PermissionError("Insufficient Spotify API permissions or unauthorized user")
                elif e.response.status_code == 400:
                    print(f"[ERROR] Bad request. This could be due to:")
                    print(f"  - Invalid authorization code")
                    print(f"  - Code already used")
                    print(f"  - Redirect URI mismatch with the one used during authorization")
                raise
            
            tokens = response.json()
            logger.debug("Successfully received tokens from Spotify")
            print(f"[DEBUG] Successfully received tokens from Spotify")
            print(f"[DEBUG] Access token length: {len(tokens.get('access_token', ''))}")
            print(f"[DEBUG] Refresh token received: {'Yes' if 'refresh_token' in tokens else 'No'}")
            print(f"[DEBUG] Token expires in: {tokens.get('expires_in', 'N/A')} seconds")
            return tokens

        except Exception as e:
            logger.error(f"Error getting Spotify tokens: {str(e)}")
            print(f"\n[ERROR] Failed to get Spotify tokens: {str(e)}")
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
            print(f"\n[DEBUG] Fetching user profile from Spotify")
            print(f"[DEBUG] Access token length: {len(self.access_token) if self.access_token else 'No token'}")
            
            response = self.session.get(f'{self.API_BASE_URL}/me')
            print(f"[DEBUG] Profile response status: {response.status_code}")
            
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                error_details = e.response.json() if e.response.content else {}
                logger.error(f"Spotify API Error: {e.response.status_code} - {e.response.text}")
                print(f"\n[ERROR] Spotify API Error when fetching profile: {e.response.status_code}")
                print(f"[ERROR] Error details: {error_details}")
                
                if e.response.status_code == 403:
                    print(f"[ERROR] Permission denied when accessing profile. This could be due to:")
                    print(f"  - Missing 'user-read-private' or 'user-read-email' scopes")
                    print(f"  - App in development mode (only authorized users can connect)")
                    raise PermissionError("Insufficient Spotify API permissions or unauthorized user")
                elif e.response.status_code == 401 and self.refresh_token:
                    print(f"[DEBUG] Token expired, attempting to refresh")
                    # Try to refresh the token and retry
                    token_data = self.refresh_token()
                    if token_data:
                        print(f"[DEBUG] Token refresh successful, retrying profile request")
                        # Retry the request
                        response = self.session.get(f'{self.API_BASE_URL}/me')
                        response.raise_for_status()
                        return response.json()
                    else:
                        print(f"[ERROR] Token refresh failed")
                        raise PermissionError("Authentication failed and token refresh was unsuccessful")
                raise
                
            profile_data = response.json()
            print(f"[DEBUG] Successfully retrieved profile for user: {profile_data.get('id')}")
            print(f"[DEBUG] User email: {profile_data.get('email', 'Not available')}")
            print(f"[DEBUG] User country: {profile_data.get('country', 'Not available')}")
            print(f"[DEBUG] User product: {profile_data.get('product', 'Not available')}")
            return profile_data
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            print(f"\n[ERROR] Failed to get user profile: {str(e)}")
            raise

    def get_user_playlists(self, limit=50, offset=0):
        """Get the current user's playlists."""
        try:
            logger.debug(f"Fetching user playlists (limit={limit}, offset={offset})")
            response = self.session.get(
                f'{self.API_BASE_URL}/me/playlists',
                params={'limit': limit, 'offset': offset}
            )
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                logger.error(f"Spotify API Error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code == 403:
                    raise PermissionError("Insufficient Spotify API permissions or unauthorized user")
                elif e.response.status_code == 401 and self.refresh_token:
                    # Try to refresh the token and retry
                    token_data = self.refresh_token()
                    if token_data:
                        # Retry the request
                        response = self.session.get(
                            f'{self.API_BASE_URL}/me/playlists',
                            params={'limit': limit, 'offset': offset}
                        )
                        response.raise_for_status()
                        return response.json()
                    else:
                        raise PermissionError("Authentication failed and token refresh was unsuccessful")
                raise
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
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                logger.error(f"Spotify API Error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code == 403:
                    logger.warning("Permission issue detected. This might be a scope problem or account restriction.")
                    # Instead of failing, return empty result with error info
                    return {
                        'items': [],
                        'error': 'permission_denied',
                        'message': 'This account may not have the required permissions or history'
                    }
                elif e.response.status_code == 401:
                    logger.warning("Authentication issue detected. Token may have expired.")
                    # Try token refresh (if implemented in a refresh_token method)
                    if hasattr(self, 'refresh_token') and callable(self.refresh_token):
                        try:
                            new_token = self.refresh_token()
                            if new_token:
                                # Retry with new token
                                self.session.headers.update({'Authorization': f'Bearer {new_token["access_token"]}'})
                                response = self.session.get(
                                    f'{self.API_BASE_URL}/me/player/recently-played',
                                    params={'limit': limit}
                                )
                                response.raise_for_status()
                                return response.json()
                        except Exception as refresh_error:
                            logger.error(f"Token refresh failed: {refresh_error}")
                    
                    # If refresh didn't work or isn't available
                    return {
                        'items': [],
                        'error': 'authentication_error',
                        'message': 'Authentication failed. Please log in again.'
                    }
                raise
            return response.json()
        except Exception as e:
            logger.error(f"Error getting recently played tracks: {str(e)}")
            # Return an error response rather than raising an exception
            # This makes the API more resilient to different account types
            return {
                'items': [],
                'error': 'api_error',
                'message': f'Error accessing Spotify API: {str(e)}'
            }

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
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                logger.error(f"Spotify API Error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code == 403:
                    raise PermissionError("Insufficient Spotify API permissions or unauthorized user")
                raise
            return response.json()
        except Exception as e:
            logger.error(f"Error getting top artists: {str(e)}")
            raise

    def get_playlist(self, playlist_id):
        """Get a playlist by ID."""
        try:
            logger.debug(f"Fetching playlist {playlist_id}")
            response = self.session.get(f'{self.API_BASE_URL}/playlists/{playlist_id}')
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                logger.error(f"Spotify API Error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code == 403:
                    raise PermissionError("Insufficient Spotify API permissions or unauthorized user")
                raise
            return response.json()
        except Exception as e:
            logger.error(f"Error getting playlist: {str(e)}")
            raise

    def get_artist(self, artist_id):
        """Get an artist by ID."""
        try:
            logger.debug(f"Fetching artist {artist_id}")
            response = self.session.get(f'{self.API_BASE_URL}/artists/{artist_id}')
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                logger.error(f"Spotify API Error: {e.response.status_code} - {e.response.text}")
                if e.response.status_code == 403:
                    raise PermissionError("Insufficient Spotify API permissions or unauthorized user")
                raise
            return response.json()
        except Exception as e:
            logger.error(f"Error getting artist: {str(e)}")
            raise

    def refresh_token(self):
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            logger.error("No refresh token available")
            return None
            
        try:
            logger.debug("Refreshing access token")
            
            # Create authorization header
            auth_header = base64.b64encode(
                f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            
            response = requests.post(self.TOKEN_URL, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Update instance with new token
            self.access_token = token_data['access_token']
            # Update session headers
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            
            # If a new refresh token was provided, update it
            if 'refresh_token' in token_data:
                self.refresh_token = token_data['refresh_token']
                
            logger.debug("Successfully refreshed access token")
            return token_data
            
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return None
            
    def _handle_auth_error(self, response):
        """Handle 401 Unauthorized responses by refreshing the access token."""
        if response.status_code == 401:
            try:
                new_token_data = self.refresh_token()
                if new_token_data:
                    # Update session headers with new token
                    self.session.headers.update({
                        'Authorization': f'Bearer {new_token_data["access_token"]}'
                    })
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
                        
                        try:
                            response.raise_for_status()
                        except requests.HTTPError as e:
                            logger.error(f"Spotify API Error: {e.response.status_code} - {e.response.text}")
                            if e.response.status_code == 403:
                                raise PermissionError("Insufficient Spotify API permissions")
                            raise
                        
                        features_chunk = response.json().get('audio_features', [])
                        audio_features.extend([f for f in features_chunk if f])  # Filter out None values
                        break  # Success, exit the retry loop
                        
                    except Exception as e:
                        retry_count += 1
                        logger.error(f"Error fetching audio features (attempt {retry_count}): {str(e)}")
                        if retry_count >= max_retries:
                            logger.error("Max retries reached, giving up")
                            raise
            
            return {'audio_features': audio_features}
            
        except Exception as e:
            logger.error(f"Error getting track features: {str(e)}")
            raise
