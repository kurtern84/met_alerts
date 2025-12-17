#!/usr/bin/env python3
"""
Convert yr-warning-icons SVG files to base64 data URLs for const.py

Download icons from: https://nrkno.github.io/yr-warning-icons/icons.zip
Extract to ./yr-warning-icons/ directory

This script processes all SVG files and generates Python dictionary entries
for ICON_DATA_URLS with proper 48x48 sizing and 8px padding.
"""

import base64
from pathlib import Path
import re


def process_svg_file(filepath):
    """Read SVG file and convert to base64 data URL with proper sizing"""
    with open(filepath, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    # Ensure viewBox is set to -8 -8 48 48 (48x48 with 8px padding)
    if 'viewBox=' in svg_content:
        svg_content = re.sub(r'viewBox="[^"]*"', 'viewBox="-8 -8 48 48"', svg_content)
    else:
        svg_content = svg_content.replace('<svg', '<svg viewBox="-8 -8 48 48"', 1)
    
    # Ensure width and height are 48
    svg_content = re.sub(r'width="[^"]*"', 'width="48"', svg_content)
    svg_content = re.sub(r'height="[^"]*"', 'height="48"', svg_content)
    if 'width=' not in svg_content:
        svg_content = svg_content.replace('<svg', '<svg width="48" height="48"', 1)
    
    # Convert to base64
    svg_bytes = svg_content.encode('utf-8')
    base64_str = base64.b64encode(svg_bytes).decode('utf-8')
    return f'data:image/svg+xml;base64,{base64_str}'


def generate_icon_dict(svg_dir):
    """Generate dictionary of icon name -> base64 data URL"""
    icons = {}
    
    for svg_file in sorted(svg_dir.glob('*.svg')):
        # Extract name: icon-warning-avalanches-yellow.svg -> avalanches-yellow
        name = svg_file.stem.replace('icon-warning-', '')
        data_url = process_svg_file(svg_file)
        icons[name] = data_url
        print(f"Processed: {name}")
    
    return icons


def format_python_dict(icons):
    """Format icons dictionary as Python code for const.py"""
    lines = ["ICON_DATA_URLS = {"]
    
    # Group by event type
    event_types = {}
    for name in sorted(icons.keys()):
        event = name.rsplit('-', 1)[0]  # Get event type (remove color)
        if event not in event_types:
            event_types[event] = []
        event_types[event].append(name)
    
    # Output grouped by event type
    for event in sorted(event_types.keys()):
        lines.append(f"    # {event.title()} icons")
        for name in event_types[event]:
            lines.append(f'    "{name}": "{icons[name]}",')
    
    lines.append("}")
    return "\n".join(lines)


def main():
    """Main conversion process"""
    # Look for icons in yr-warning-icons directory (user should extract there)
    svg_dir = Path("yr-warning-icons\\dist\\svg")
    
    # Fallback: check icons_temp location
    if not svg_dir.exists():
        svg_dir = Path("icons_temp/dist/svg")
    
    if not svg_dir.exists():
        print(f"Error: SVG directory not found!")
        print(f"Please download: https://nrkno.github.io/yr-warning-icons/icons.zip")
        print(f"Extract to: ./yr-warning-icons/ directory")
        return
    
    print(f"Converting icons from: {svg_dir.absolute()}")
    print("-" * 60)
    
    # Generate icon dictionary
    icons = generate_icon_dict(svg_dir)
    
    if not icons:
        print("No SVG files found!")
        return
    
    print("-" * 60)
    print(f"Total icons converted: {len(icons)}")
    
    # Format as Python code
    python_code = format_python_dict(icons)
    
    # Write to output file
    output_file = Path("icon_dict_output.py")
    output_file.write_text(python_code, encoding='utf-8')
    print(f"\nOutput written to: {output_file}")
    print("\nCopy the ICON_DATA_URLS dictionary into const.py")
    
    # Show event types covered
    event_types = sorted(set(name.rsplit('-', 1)[0] for name in icons.keys()))
    print(f"\nEvent types covered ({len(event_types)}):")
    for event in event_types:
        colors = [name.split('-')[-1] for name in icons.keys() if name.startswith(event + '-')]
        print(f"  - {event}: {', '.join(colors)}")


if __name__ == "__main__":
    main()
