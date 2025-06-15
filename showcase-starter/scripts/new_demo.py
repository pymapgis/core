#!/usr/bin/env python3
"""
PyMapGIS Showcase Demo Scaffold Generator

Usage:
    python scripts/new_demo.py demo-name

This script creates a new showcase demo by copying the TEMPLATE directory
and replacing placeholders with demo-specific values.
"""

import os
import sys
import shutil
import re
from pathlib import Path
from typing import Dict, Any


# Demo configuration templates
DEMO_CONFIGS = {
    "border-flow": {
        "title": "Border Flow Now",
        "description": "Real-time truck wait times at border crossings",
        "data_url": "https://bwt.cbp.gov/api/bwtdata",
        "backup_data_url": "",
        "category": "logistics",
        "layer_name": "border_crossings",
        "icon": "🚛",
        "data_source": "CBP Border Wait Times",
        "legend_title": "Wait Time",
        "default_lon": -100.0,
        "default_lat": 32.0,
        "default_zoom": 4,
        "color_low": "#00ff00",
        "color_medium": "#ffff00", 
        "color_high": "#ff8000",
        "color_extreme": "#ff0000",
        "range_low_max": 30,
        "range_medium_max": 60,
        "range_high_max": 120,
        "range_extreme_max": 240,
        "range_low": "0-30 min",
        "range_medium": "30-60 min",
        "range_high": "60-120 min",
        "range_extreme": "120+ min",
        "update_frequency": "Every 15 minutes",
        "coverage": "US-Mexico and US-Canada borders"
    },
    "flight-delay": {
        "title": "Flight Delay Now",
        "description": "Live airport delay visualization",
        "data_url": "https://soa.smext.faa.gov/asws/api/airport/status",
        "backup_data_url": "",
        "category": "transportation",
        "layer_name": "airports",
        "icon": "✈️",
        "data_source": "FAA System Operations",
        "legend_title": "Delay Minutes",
        "default_lon": -95.0,
        "default_lat": 39.0,
        "default_zoom": 4,
        "color_low": "#00bfff",
        "color_medium": "#ffff00",
        "color_high": "#ff7e00", 
        "color_extreme": "#ff0000",
        "range_low_max": 15,
        "range_medium_max": 30,
        "range_high_max": 60,
        "range_extreme_max": 120,
        "range_low": "0-15 min",
        "range_medium": "15-30 min", 
        "range_high": "30-60 min",
        "range_extreme": "60+ min",
        "update_frequency": "Every 10 minutes",
        "coverage": "Major US airports"
    },
    "wildfire-risk": {
        "title": "Wildfire Risk Now",
        "description": "Fire danger and population exposure assessment",
        "data_url": "https://firms.modaps.eosdis.nasa.gov/api/area/csv/viirs-snpp/world/1",
        "backup_data_url": "",
        "category": "emergency",
        "layer_name": "fire_risk",
        "icon": "🔥",
        "data_source": "NASA FIRMS + Census",
        "legend_title": "Risk Level",
        "default_lon": -120.0,
        "default_lat": 37.0,
        "default_zoom": 6,
        "color_low": "#90EE90",
        "color_medium": "#FFD700",
        "color_high": "#FF8C00",
        "color_extreme": "#DC143C",
        "range_low_max": 2,
        "range_medium_max": 4,
        "range_high_max": 6,
        "range_extreme_max": 8,
        "range_low": "Low",
        "range_medium": "Moderate",
        "range_high": "High", 
        "range_extreme": "Extreme",
        "update_frequency": "Every 3 hours",
        "coverage": "Global"
    }
}


def get_demo_config(demo_name: str) -> Dict[str, Any]:
    """Get configuration for a demo, with fallback to generic template."""
    if demo_name in DEMO_CONFIGS:
        return DEMO_CONFIGS[demo_name]
    
    # Generic template for custom demos
    return {
        "title": demo_name.replace("-", " ").title(),
        "description": f"Live {demo_name.replace('-', ' ')} visualization",
        "data_url": "https://example.com/api/data.json",
        "backup_data_url": "",
        "category": "general",
        "layer_name": demo_name.replace("-", "_"),
        "icon": "🌍",
        "data_source": "Public Data Source",
        "legend_title": "Score",
        "default_lon": 0.0,
        "default_lat": 0.0,
        "default_zoom": 2,
        "color_low": "#00bfff",
        "color_medium": "#ffff00",
        "color_high": "#ff7e00",
        "color_extreme": "#ff0000",
        "range_low_max": 2,
        "range_medium_max": 4,
        "range_high_max": 6,
        "range_extreme_max": 8,
        "range_low": "Low",
        "range_medium": "Medium",
        "range_high": "High",
        "range_extreme": "Extreme",
        "update_frequency": "Every hour",
        "coverage": "Global"
    }


def replace_placeholders(content: str, config: Dict[str, Any]) -> str:
    """Replace template placeholders with actual values."""
    replacements = {
        "{{DEMO_TITLE}}": config["title"],
        "{{DESCRIPTION}}": config["description"],
        "{{DATA_URL}}": config["data_url"],
        "{{BACKUP_DATA_URL}}": config["backup_data_url"],
        "{{CATEGORY}}": config["category"],
        "{{LAYER_NAME}}": config["layer_name"],
        "{{ICON}}": config["icon"],
        "{{DATA_SOURCE}}": config["data_source"],
        "{{LEGEND_TITLE}}": config["legend_title"],
        "{{DEFAULT_LON}}": str(config["default_lon"]),
        "{{DEFAULT_LAT}}": str(config["default_lat"]),
        "{{DEFAULT_ZOOM}}": str(config["default_zoom"]),
        "{{COLOR_LOW}}": config["color_low"],
        "{{COLOR_MEDIUM}}": config["color_medium"],
        "{{COLOR_HIGH}}": config["color_high"],
        "{{COLOR_EXTREME}}": config["color_extreme"],
        "{{RANGE_LOW_MAX}}": str(config["range_low_max"]),
        "{{RANGE_MEDIUM_MAX}}": str(config["range_medium_max"]),
        "{{RANGE_HIGH_MAX}}": str(config["range_high_max"]),
        "{{RANGE_EXTREME_MAX}}": str(config["range_extreme_max"]),
        "{{RANGE_LOW}}": config["range_low"],
        "{{RANGE_MEDIUM}}": config["range_medium"],
        "{{RANGE_HIGH}}": config["range_high"],
        "{{RANGE_EXTREME}}": config["range_extreme"],
        "{{UPDATE_FREQUENCY}}": config["update_frequency"],
        "{{COVERAGE}}": config["coverage"]
    }
    
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    
    return content


def create_demo(demo_name: str) -> None:
    """Create a new demo from the template."""
    # Validate demo name
    if not re.match(r'^[a-z0-9-]+$', demo_name):
        print("❌ Demo name must contain only lowercase letters, numbers, and hyphens")
        sys.exit(1)
    
    # Get paths
    script_dir = Path(__file__).parent
    showcase_dir = script_dir.parent
    template_dir = showcase_dir / "TEMPLATE"
    showcases_dir = showcase_dir / "showcases"
    demo_dir = showcases_dir / demo_name
    
    # Check if template exists
    if not template_dir.exists():
        print(f"❌ Template directory not found: {template_dir}")
        sys.exit(1)
    
    # Check if demo already exists
    if demo_dir.exists():
        print(f"❌ Demo '{demo_name}' already exists at {demo_dir}")
        sys.exit(1)
    
    # Create showcases directory if it doesn't exist
    showcases_dir.mkdir(exist_ok=True)
    
    # Get demo configuration
    config = get_demo_config(demo_name)
    
    print(f"🚀 Creating demo: {config['title']}")
    print(f"📁 Location: {demo_dir}")
    
    # Copy template directory
    shutil.copytree(template_dir, demo_dir)
    
    # Process all files in the demo directory
    for root, dirs, files in os.walk(demo_dir):
        for file in files:
            file_path = Path(root) / file
            
            # Skip binary files
            if file_path.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.ico']:
                continue
            
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace placeholders
                updated_content = replace_placeholders(content, config)
                
                # Write back if changed
                if updated_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    print(f"✅ Updated: {file_path.relative_to(demo_dir)}")
                
            except Exception as e:
                print(f"⚠️  Warning: Could not process {file_path}: {e}")
    
    # Create a README for the demo
    readme_content = f"""# {config['title']}

{config['description']}

## Data Source
- **URL**: {config['data_url']}
- **Update Frequency**: {config['update_frequency']}
- **Coverage**: {config['coverage']}

## Quick Start

```bash
# Build and run
docker build -t {demo_name} .
docker run -p 8000:8000 {demo_name}

# Open http://localhost:8000
```

## Development

```bash
# Run locally
python worker.py
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Customization

Edit these files to customize your demo:
- `worker.py` - Data processing logic
- `static/app.js` - Map styling and interactions
- `static/index.html` - UI layout and content

## Contributing

This demo was generated from the PyMapGIS showcase template.
See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.
"""
    
    with open(demo_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Created README.md")
    
    # Success message
    print(f"\n🎉 Demo '{demo_name}' created successfully!")
    print(f"\n📋 Next steps:")
    print(f"1. cd showcases/{demo_name}")
    print(f"2. Edit worker.py to implement your data processing logic")
    print(f"3. Customize static/app.js for map styling")
    print(f"4. Test with: docker build -t {demo_name} . && docker run -p 8000:8000 {demo_name}")
    print(f"5. Open http://localhost:8000 to see your demo")
    print(f"\n📖 See CONTRIBUTING.md for detailed guidelines")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/new_demo.py <demo-name>")
        print("\nAvailable pre-configured demos:")
        for name, config in DEMO_CONFIGS.items():
            print(f"  {name} - {config['title']}")
        print("\nOr use any custom name (lowercase, hyphens allowed)")
        sys.exit(1)
    
    demo_name = sys.argv[1].lower()
    create_demo(demo_name)


if __name__ == "__main__":
    main()
