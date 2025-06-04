#!/usr/bin/env python3
"""
Simple icon generator for Chrome extension
Creates basic icon files with a book/reading theme
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_icon(size, filename):
    """Create a single icon of specified size"""
    # Create a new image with transparent background
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Define colors
    bg_color = (175, 80, 76, 255)
    book_color = (255, 255, 255, 255)  # White book
    accent_color = (46, 125, 50, 255)  # Darker green for accent

    # Draw circular background
    margin = max(1, size // 16)
    draw.ellipse([margin, margin, size - margin, size - margin], fill=bg_color)

    # Calculate book dimensions based on icon size
    book_width = size // 3
    book_height = size // 2
    book_x = (size - book_width) // 2
    book_y = (size - book_height) // 2

    # Draw book shape
    # Main book rectangle
    draw.rectangle(
        [book_x, book_y, book_x + book_width, book_y + book_height],
        fill=book_color,
        outline=accent_color,
        width=max(1, size // 32),
    )

    # Book spine line
    spine_x = book_x + book_width // 8
    draw.line(
        [spine_x, book_y, spine_x, book_y + book_height],
        fill=accent_color,
        width=max(1, size // 32),
    )

    # Book pages (small lines)
    if size >= 32:  # Only add details for larger icons
        page_spacing = book_height // 6
        for i in range(3):
            page_y = book_y + page_spacing * (i + 1)
            draw.line(
                [
                    book_x + book_width // 4,
                    page_y,
                    book_x + book_width - book_width // 8,
                    page_y,
                ],
                fill=accent_color,
                width=max(1, size // 64),
            )

    # Add bookmark ribbon for larger icons
    if size >= 48:
        ribbon_width = max(2, size // 32)
        ribbon_x = book_x + book_width - ribbon_width
        ribbon_top = book_y - size // 16
        ribbon_bottom = book_y + book_height // 3

        # Ribbon rectangle
        draw.rectangle(
            [ribbon_x, ribbon_top, ribbon_x + ribbon_width, ribbon_bottom],
            fill=(244, 67, 54, 255),
        )  # Red ribbon

        # Ribbon tail (triangle)
        triangle_height = size // 16
        draw.polygon(
            [
                (ribbon_x, ribbon_bottom),
                (ribbon_x + ribbon_width, ribbon_bottom),
                (ribbon_x + ribbon_width // 2, ribbon_bottom + triangle_height),
            ],
            fill=(244, 67, 54, 255),
        )

    # Save the image
    img.save(filename, "PNG")
    print(f"Created {filename} ({size}x{size})")


def main():
    """Generate all required icon sizes"""
    print("Generating Chrome extension icons...")

    # Check if PIL is available
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("Error: Pillow library is required.")
        print("Install it with: pip install Pillow")
        return

    # Icon sizes required by Chrome extensions
    sizes = [192, 512]

    # Create icons directory if it doesn't exist
    if not os.path.exists("icons"):
        os.makedirs("icons")
        print("Created 'icons' directory")

    # Generate each icon size
    for size in sizes:
        filename = f"icons/icon-{size}x{size}.png"
        create_icon(size, filename)

    print("\nAll icons generated successfully!")
    print("Files created:")
    for size in sizes:
        print(f"  - icon{size}.png")

    print("\nYou can now use these icons in your Chrome extension manifest.json")


if __name__ == "__main__":
    main()
