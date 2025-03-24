#!/bin/bash

# Create a base green square with Spotify logo for our icon
convert -size 512x512 xc:#1DB954 \
    -font "FontAwesome" -pointsize 384 -fill white -gravity center \
    -draw "text 0,0 '\uf1bc'" \
    base_icon.png

# Generate different sizes for PWA
sizes=(72 96 128 144 152 192 384 512)
for size in "${sizes[@]}"; do
    convert base_icon.png -resize ${size}x${size} icon-${size}x${size}.png
done

# Generate favicon sizes
convert base_icon.png -resize 16x16 favicon-16x16.png
convert base_icon.png -resize 32x32 favicon-32x32.png
convert base_icon.png -resize 180x180 apple-touch-icon.png
convert base_icon.png -resize 192x192 android-chrome-192x192.png
convert base_icon.png -resize 512x512 android-chrome-512x512.png

# Create favicon.ico with multiple sizes
convert favicon-16x16.png favicon-32x32.png favicon.ico

# Clean up base icon
rm base_icon.png

echo "Icon generation complete!"