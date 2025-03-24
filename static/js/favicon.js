// Create a temporary canvas to generate favicon
(function() {
    const canvas = document.createElement('canvas');
    canvas.width = 32;
    canvas.height = 32;
    const ctx = canvas.getContext('2d');

    // Draw green background
    ctx.fillStyle = '#1DB954';
    ctx.fillRect(0, 0, 32, 32);

    // Draw 'S' letter in white
    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 24px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('S', 16, 16);

    // Convert to blob and create object URL
    canvas.toBlob(function(blob) {
        const faviconLink = document.querySelector('link[rel="icon"]');
        if (faviconLink) {
            faviconLink.href = URL.createObjectURL(blob);
        }
    });
})();