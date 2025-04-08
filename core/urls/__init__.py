# This file makes the urls directory a Python package
# Import patterns from core_urls.py to avoid circular imports
from .core_urls import urlpatterns, app_name
