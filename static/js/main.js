// Utility functions
const spotifyUtils = {
    formatDuration(milliseconds) {
        const minutes = Math.floor(milliseconds / 60000);
        const seconds = ((milliseconds % 60000) / 1000).toFixed(0);
        return `${minutes}:${seconds.padStart(2, '0')}`;
    },

    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }
};

// Chart configurations and utilities
const chartConfigs = {
    colors: [
        '#1DB954', // Spotify green
        '#1ED760', // Lighter green
        '#2EBD59', // Alternative green
        '#57B660', // Muted green
        '#78B159', // Pale green
        '#191414', // Spotify black
        '#282828', // Dark gray
        '#404040', // Medium gray
    ],

    commonOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    font: { size: 12 }
                }
            }
        }
    },

    createGenreChart(ctx, data) {
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: this.colors,
                    borderWidth: 1
                }]
            },
            options: {
                ...this.commonOptions,
                plugins: {
                    ...this.commonOptions.plugins,
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.label}: ${context.raw}%`
                        }
                    }
                }
            }
        });
    },

    createFeaturesChart(ctx, data) {
        // Add null/undefined check before trying to use data
        if (!data || typeof data !== 'object') {
            console.warn('Audio features data is null, undefined, or not an object');
            return null; // Return null instead of creating a chart with invalid data
        }

        return new Chart(ctx, {
            type: 'radar',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Audio Features',
                    data: Object.values(data),
                    backgroundColor: 'rgba(29, 185, 84, 0.2)',
                    borderColor: '#1DB954',
                    pointBackgroundColor: '#1DB954'
                }]
            },
            options: {
                ...this.commonOptions,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.2)' },
                        grid: { color: 'rgba(255, 255, 255, 0.2)' },
                        pointLabels: { color: '#666' },
                        ticks: { 
                            beginAtZero: true,
                            max: 1,
                            stepSize: 0.2
                        }
                    }
                }
            }
        });
    }
};

// Spotify API wrapper
class SpotifyApi {
    async getTrends() {
        const response = await fetch('/api/trends/');
        if (!response.ok) {
            throw new Error('Failed to fetch trends');
        }
        return response.json();
    }

    async getUserAnalytics() {
        const response = await fetch('/api/user/analytics/');
        if (!response.ok) {
            throw new Error('Failed to fetch user analytics');
        }
        return response.json();
    }

    async getPlaylistAnalysis(playlistId) {
        const response = await fetch(`/api/playlists/${playlistId}/`);
        if (!response.ok) {
            throw new Error('Failed to fetch playlist analysis');
        }
        return response.json();
    }
}

// Initialize global spotifyApi instance and make it available immediately
// This ensures it's defined before any page-specific scripts run
window.spotifyApi = new SpotifyApi();

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // Initialize Bootstrap popovers
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(popover => {
        new bootstrap.Popover(popover);
    });

    // Handle collapsible elements
    document.querySelectorAll('[data-toggle="collapse"]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.dataset.target);
            if (target) {
                target.classList.toggle('show');
            }
        });
    });
    
    // Dispatch a custom event to notify page-specific scripts that main.js has loaded
    // This allows page scripts to wait for this event if they need to use spotifyApi
    document.dispatchEvent(new Event('mainJsLoaded'));
});

// Chart update functions
function updateGenreDistribution(data) {
    const ctx = document.getElementById('genreDistribution')?.getContext('2d');
    if (ctx) {
        chartConfigs.createGenreChart(ctx, {
            labels: Object.keys(data),
            values: Object.values(data)
        });
    }
}

function updateAudioFeatures(data) {
    const ctx = document.getElementById('audioFeatures')?.getContext('2d');
    if (ctx) {
        chartConfigs.createFeaturesChart(ctx, data);
    }
}

// Simple error handling
function showError(message, container) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        ${message}
    `;
    if (container) {
        container.appendChild(errorDiv);
    } else {
        document.body.appendChild(errorDiv);
    }
}