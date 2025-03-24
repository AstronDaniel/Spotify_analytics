from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def format_duration(milliseconds):
    """
    Format milliseconds into a human-readable duration.
    Example: 214032 -> "3:34"
    """
    if not milliseconds:
        return "0:00"
    
    seconds = int(milliseconds / 1000)
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}:{minutes:02d}:{remaining_seconds:02d}"
    
    return f"{minutes}:{remaining_seconds:02d}"

@register.filter
def format_duration_long(milliseconds):
    """
    Format milliseconds into a long human-readable duration.
    Example: 214032 -> "3 minutes, 34 seconds"
    """
    if not milliseconds:
        return "0 seconds"
    
    delta = timedelta(milliseconds=milliseconds)
    hours = delta.seconds // 3600
    minutes = (delta.seconds // 60) % 60
    seconds = delta.seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    return ", ".join(parts)

@register.filter
def percentage(value, total):
    """
    Calculate percentage and format it.
    """
    try:
        return f"{(float(value) / float(total) * 100):.1f}%"
    except (ValueError, ZeroDivisionError):
        return "0%"

@register.filter
def format_key(key_number):
    """
    Convert musical key number to human-readable format.
    Spotify uses 0-11 for keys (0 = C, 1 = C♯/D♭, etc.)
    """
    keys = ['C', 'C♯/D♭', 'D', 'D♯/E♭', 'E', 'F', 
            'F♯/G♭', 'G', 'G♯/A♭', 'A', 'A♯/B♭', 'B']
    try:
        return keys[int(key_number)]
    except (ValueError, IndexError):
        return "Unknown"

@register.filter
def format_mode(mode_number):
    """
    Convert mode number to text (0 = minor, 1 = major).
    """
    modes = {0: 'Minor', 1: 'Major'}
    return modes.get(int(mode_number), 'Unknown')

@register.filter
def format_popularity(value):
    """
    Format popularity score with appropriate label.
    """
    try:
        score = int(value)
        if score >= 80:
            return f"{score} (Very Popular)"
        elif score >= 60:
            return f"{score} (Popular)"
        elif score >= 40:
            return f"{score} (Moderate)"
        else:
            return f"{score} (Niche)"
    except ValueError:
        return "Unknown"

@register.simple_tag
def audio_feature_description(feature_name):
    """
    Return description for Spotify audio features.
    """
    descriptions = {
        'danceability': 'How suitable a track is for dancing',
        'energy': 'Perceptual measure of intensity and activity',
        'key': 'The key the track is in',
        'loudness': 'Overall loudness in decibels (dB)',
        'mode': 'Modality (major or minor)',
        'speechiness': 'Presence of spoken words',
        'acousticness': 'Whether the track is acoustic',
        'instrumentalness': 'Predicts whether a track contains no vocals',
        'liveness': 'Detects presence of an audience in the recording',
        'valence': 'Musical positiveness conveyed by a track',
        'tempo': 'Overall estimated tempo in beats per minute (BPM)',
    }
    return descriptions.get(feature_name, '')