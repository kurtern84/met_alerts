"""Generate base64-encoded icon data URLs for embedding."""
import base64
from pathlib import Path

icons_dir = Path(__file__).parent / "icons"
output = {}

for svg_file in sorted(icons_dir.glob("icon-warning-*.svg")):
    # Read SVG content
    with open(svg_file, "rb") as f:
        svg_data = f.read()
    
    # Encode to base64
    b64_data = base64.b64encode(svg_data).decode("utf-8")
    data_url = f"data:image/svg+xml;base64,{b64_data}"
    
    # Extract key from filename: icon-warning-wind-yellow.svg -> wind-yellow
    key = svg_file.stem.replace("icon-warning-", "")
    
    output[key] = data_url
    print(f'    "{key}": "{data_url}",')

print(f"\nTotal icons: {len(output)}")
