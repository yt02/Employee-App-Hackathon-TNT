"""
Simple icon generator for PWA
Creates placeholder icons in different sizes
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Icon sizes needed for PWA
SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Colors
BG_COLOR = (102, 126, 234)  # #667eea
TEXT_COLOR = (255, 255, 255)

def create_icon(size, output_path):
    """Create a simple icon with text"""
    # Create image with gradient-like background
    img = Image.new('RGB', (size, size), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Add a simple design - circle with text
    margin = size // 10
    draw.ellipse([margin, margin, size-margin, size-margin], 
                 fill=(118, 75, 162))  # #764ba2
    
    # Add text "EMS"
    try:
        # Try to use a system font
        font_size = size // 3
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    text = "EMS"
    
    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)
    
    # Save the icon
    img.save(output_path, 'PNG')
    print(f"Created icon: {output_path}")

def main():
    """Generate all icon sizes"""
    icons_dir = os.path.join('app', 'static', 'icons')
    
    # Create icons directory if it doesn't exist
    os.makedirs(icons_dir, exist_ok=True)
    
    # Generate icons
    for size in SIZES:
        filename = f'icon-{size}x{size}.png'
        output_path = os.path.join(icons_dir, filename)
        create_icon(size, output_path)
    
    print(f"\n✅ Successfully generated {len(SIZES)} icons!")
    print(f"Icons saved to: {icons_dir}")

if __name__ == '__main__':
    main()

