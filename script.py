from PIL import Image, ImageDraw, ImageFont
import random
import string


def generate_favicon(text="KN", size=32, font_size=25, output_path="favicon.ico"):
    # Generate a random background color
    bg_color = (255, 255, 255)
    # Set text color to be contrasting (white or black)
    text_color = (0, 0, 0)

    # Create the image
    image = Image.new("RGB", (size, size), color=bg_color)
    draw = ImageDraw.Draw(image)

    # Try to load a TTF font, fallback to default
    try:
        font = ImageFont.truetype("Outfit-VariableFont_wght.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Get bounding box of text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center the text
    position = ((size - text_width) // 2, (size - text_height) // 2)

    # Draw the text
    draw.text(position, text, fill=text_color, font=font)

    # Save as favicon
    image.save(output_path, format="ICO")
    print(f"✅ Favicon generated: {output_path}")


# Example: Generate a favicon with 2 random letters
generate_favicon()
