# We're moving URL patterns to a package structure
# This file now simply imports from the package
from .urls.core_urls import urlpatterns, app_name

# This file is now a simple redirect to avoid conflicts