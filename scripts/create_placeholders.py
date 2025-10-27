"""
Create placeholder images for testing the site
This script generates simple colored placeholder images so you can see the layout
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder(width, height, color, text, filename):
    """Create a placeholder image with text"""
    # Create image
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)

    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", size=40)
    except:
        font = ImageFont.load_default()

    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((width - text_width) // 2, (height - text_height) // 2)

    # Draw text
    draw.text(position, text, fill='white', font=font)

    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Save image
    img.save(filename)
    print(f"Created: {filename}")

# Create directories
os.makedirs('static/images/logo', exist_ok=True)
os.makedirs('static/images/hero', exist_ok=True)
os.makedirs('static/images/categories', exist_ok=True)
os.makedirs('static/images/gallery', exist_ok=True)

print("Creating placeholder images...")
print("=" * 50)

# Logo
create_placeholder(500, 150, '#6366f1', "Snow Spoiled Gifts",
                   'static/images/logo/logo-main.png')

# Hero banner
create_placeholder(1920, 600, '#8b5cf6', 'Coming Soon!',
                   'static/images/hero/hero-banner.jpg')

# Category images
create_placeholder(600, 400, '#6366f1', '3D Printing',
                   'static/images/categories/3d-printing.jpg')
create_placeholder(600, 400, '#ec4899', 'Sublimation',
                   'static/images/categories/sublimation.jpg')
create_placeholder(600, 400, '#14b8a6', 'Vinyl',
                   'static/images/categories/vinyl.jpg')
create_placeholder(600, 400, '#f59e0b', 'Giftboxes',
                   'static/images/categories/giftboxes.jpg')

# Gallery images
colors = ['#6366f1', '#ec4899', '#14b8a6', '#f59e0b', '#8b5cf6', '#06b6d4']
for i in range(1, 7):
    create_placeholder(600, 600, colors[i-1], f'Preview {i}',
                       f'static/images/gallery/preview-{i}.jpg')

print("=" * 50)
print("✓ All placeholder images created!")
print("\nYou can now run the site and see the layout with placeholder images.")
print("Replace these with your actual images when ready.")
