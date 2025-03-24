from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.conf import settings
import os
import json

User = get_user_model()

class Command(BaseCommand):
    help = 'Sets up development environment with test data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting development environment setup...'))

        try:
            # Run migrations
            self.stdout.write('Applying migrations...')
            call_command('migrate')

            # Create superuser if it doesn't exist
            if not User.objects.filter(username='admin').exists():
                self.stdout.write('Creating superuser...')
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123'
                )

            # Load initial data fixtures
            self.stdout.write('Loading initial data...')
            call_command('loaddata', 'initial_data')

            # Create required directories
            self.stdout.write('Creating required directories...')
            directories = [
                os.path.join(settings.BASE_DIR, 'static'),
                os.path.join(settings.BASE_DIR, 'static', 'css'),
                os.path.join(settings.BASE_DIR, 'static', 'js'),
                os.path.join(settings.BASE_DIR, 'static', 'img'),
                os.path.join(settings.BASE_DIR, 'media'),
            ]
            
            for directory in directories:
                if not os.path.exists(directory):
                    os.makedirs(directory)

            # Create sample .env file if it doesn't exist
            env_template_path = os.path.join(settings.BASE_DIR, '.env.template')
            env_path = os.path.join(settings.BASE_DIR, '.env')
            
            if not os.path.exists(env_path) and os.path.exists(env_template_path):
                self.stdout.write('Creating .env file from template...')
                with open(env_template_path, 'r') as template_file:
                    with open(env_path, 'w') as env_file:
                        env_file.write(template_file.read())

            # Collect static files
            self.stdout.write('Collecting static files...')
            call_command('collectstatic', '--noinput')

            # Create cache tables
            self.stdout.write('Creating cache tables...')
            call_command('createcachetable')

            self.stdout.write(self.style.SUCCESS('''
Development environment setup complete!

You can now:
1. Update the .env file with your Spotify API credentials
2. Run the development server: python manage.py runserver
3. Access the admin interface at: http://localhost:8000/admin
   Username: admin
   Password: admin123

Remember to change the admin password in production!
'''))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during setup: {str(e)}')
            )
            raise

    def create_sample_env(self):
        """Create a sample .env file with development settings"""
        env_content = """
# Django Settings
DJANGO_SECRET_KEY=development-secret-key-change-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=spotify_analytics
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis Cache Configuration
REDIS_URL=redis://127.0.0.1:6379/1

# Spotify API Configuration
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
SPOTIFY_REDIRECT_URI=http://localhost:8000/spotify/callback
"""
        with open(os.path.join(settings.BASE_DIR, '.env'), 'w') as f:
            f.write(env_content.strip())