# Spotify Analytics Platform

# Spotify Analytics Platform

**A powerful insights engine that transforms music streaming data into actionable intelligence**

## What It Does

The Spotify Analytics Platform leverages the Spotify API to provide comprehensive insights into listening patterns, helping users discover trends and understand their music preferences with unprecedented depth. Our platform processes and visualizes music data through:

- **Deep playlist analysis** - Uncover patterns in your curated collections
- **Personal listening insights** - Understand your unique music journey
- **Music trend visualization** - See what's trending globally and in your network
- **Audio feature analysis** - Explore the technical aspects of your music tastes

## Technical Excellence

Built with a robust stack designed for performance and scalability:

- **Backend**: Django + Django REST Framework
- **Frontend**: Responsive design with Bootstrap 5 and Chart.js
- **Data Infrastructure**: PostgreSQL database with Redis caching
- **API Integration**: Seamless connection with Spotify Web API
- **Real-time Processing**: Live updates of listening patterns

## Why It Matters

In today's data-driven world, music analytics provide more than entertainment—they offer insights into culture, personal psychology, and global trends. Our platform transforms raw streaming data into meaningful visualizations that tell the story behind the music.

## The Vision

Beyond personal use, we're creating a platform that musicians, industry professionals, and researchers can leverage to better understand audiences and make data-driven decisions about music creation and promotion.

---

*Developed by AstronDaniel - Transforming music listening from passive consumption to active exploration*
## Features

- 🎵 Deep playlist analysis
- 📊 Music trend visualization
- 👤 Personal listening insights 
- 🌐 Public music trends
- 📱 Responsive design
- 📈 Detailed audio feature analysis
- 🎨 Genre distribution analysis
- 🎸 Artist popularity metrics
- 🔄 Real-time data processing
- 📤 Export and sharing capabilities

## Technology Stack

- **Backend**: Django + Django REST Framework
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **Caching**: Redis
- **API**: Spotify Web API
- **Charts**: Chart.js
- **CSS Framework**: Bootstrap 5

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Node.js (for development)
- Spotify Developer Account

## Setup

1. Clone the repository:
```bash
git clone https://github.com/AstronDaniel /spotify-analytics.git
cd spotify-analytics
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# OR
source venv/bin/activate      # Unix/MacOS
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment template and configure:
```bash
cp .env.template .env
```
Edit `.env` file with your settings:
- Add Django secret key
- Configure database settings
- Add Spotify API credentials

5. Set up the database:
```bash
python manage.py migrate
```

6. Create superuser (admin):
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Environment Variables

Required environment variables in `.env`:

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=spotify_analytics
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
SPOTIFY_REDIRECT_URI=http://localhost:8000/spotify/callback
```

## Project Structure

```
spotify_analytics/
├── analytics/          # Analytics processing app
├── api/               # API endpoints
├── core/              # Core functionality
├── users/             # User management
├── static/            # Static files
│   ├── css/
│   ├── js/
│   └── img/
├── templates/         # HTML templates
├── spotify_analytics/ # Project settings
└── manage.py         # Django management
```

## API Endpoints

### Public Endpoints
- `GET /api/trends/` - Get public music trends
- `GET /api/artists/` - Get artist analysis
- `GET /api/tracks/` - Get track features

### Authenticated Endpoints
- `GET /api/playlists/` - List user playlists
- `GET /api/playlists/{id}/` - Get playlist analysis
- `GET /api/user/analytics/` - Get user analytics
- `POST /api/auth/spotify/` - Spotify authentication

## Development

1. Run tests:
```bash
python manage.py test
```

2. Check code style:
```bash
flake8
```

3. Generate migrations:
```bash
python manage.py makemigrations
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Spotify Web API
- Django Documentation
- Chart.js Documentation
