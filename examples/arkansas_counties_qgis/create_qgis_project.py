#!/usr/bin/env python3
"""
Create QGIS Project for Arkansas Counties

This script creates a complete QGIS project programmatically using PyQGIS.
It demonstrates how to:
1. Load Arkansas counties data
2. Style the layer with colors and labels
3. Set up the map canvas
4. Save a complete QGIS project file

Requirements:
- QGIS must be installed
- Run this script in a QGIS Python environment

Author: PyMapGIS Team
"""

import sys
import os
from pathlib import Path

# Check if we're running in QGIS environment
try:
    from qgis.core import (
        QgsApplication,
        QgsVectorLayer,
        QgsProject,
        QgsSymbol,
        QgsRendererCategory,
        QgsCategorizedSymbolRenderer,
        QgsSimpleFillSymbolLayer,
        QgsTextFormat,
        QgsVectorLayerSimpleLabeling,
        QgsPalLayerSettings,
        QgsCoordinateReferenceSystem,
        QgsRectangle,
        QgsMapSettings,
        QgsLayoutManager,
        QgsPrintLayout,
        QgsLayoutItemMap,
        QgsLayoutPoint,
        QgsLayoutSize,
        QgsUnitTypes
    )
    from qgis.PyQt.QtCore import QVariant
    from qgis.PyQt.QtGui import QColor, QFont
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False
    print("❌ QGIS not available. This script requires QGIS to be installed.")
    print("   Install QGIS and run this script in the QGIS Python environment.")

# Configuration
DATA_DIR = Path(__file__).parent / "data"
ARKANSAS_GPKG = DATA_DIR / "arkansas_counties.gpkg"
PROJECT_PATH = DATA_DIR / "arkansas_counties_project.qgz"

def check_prerequisites():
    """Check if all required files and dependencies are available."""
    if not QGIS_AVAILABLE:
        print("❌ QGIS is not available")
        return False
    
    if not ARKANSAS_GPKG.exists():
        print(f"❌ Arkansas counties data not found: {ARKANSAS_GPKG}")
        print("   Run arkansas_counties_example.py first to download the data")
        return False
    
    print("✅ All prerequisites met")
    return True

def initialize_qgis():
    """Initialize QGIS application."""
    print("🚀 Initializing QGIS...")
    
    # Create QGIS application
    # The [] argument is for command line arguments
    # False means we don't want a GUI
    qgs = QgsApplication([], False)
    
    # Set the QGIS prefix path (adjust if needed)
    # This is usually automatically detected
    qgs.initQgis()
    
    print("✅ QGIS initialized")
    return qgs

def load_arkansas_counties():
    """Load Arkansas counties layer."""
    print("📂 Loading Arkansas counties data...")
    
    # Create vector layer
    layer = QgsVectorLayer(str(ARKANSAS_GPKG), "Arkansas Counties", "ogr")
    
    if not layer.isValid():
        print(f"❌ Failed to load layer from {ARKANSAS_GPKG}")
        return None
    
    print(f"✅ Loaded {layer.featureCount()} counties")
    return layer

def style_counties_layer(layer):
    """Apply styling to the counties layer."""
    print("🎨 Styling counties layer...")
    
    # Create a simple fill symbol
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    
    # Set fill color and outline
    symbol.setColor(QColor(173, 216, 230))  # Light blue
    symbol.symbolLayer(0).setStrokeColor(QColor(0, 0, 0))  # Black outline
    symbol.symbolLayer(0).setStrokeWidth(0.5)
    
    # Apply the symbol to the layer
    layer.renderer().setSymbol(symbol)
    
    # Add labels
    add_county_labels(layer)
    
    print("✅ Styling applied")

def add_county_labels(layer):
    """Add county name labels to the layer."""
    print("🏷️  Adding county labels...")
    
    # Create label settings
    label_settings = QgsPalLayerSettings()
    
    # Set the field to use for labels
    label_settings.fieldName = "NAME"
    
    # Set text format
    text_format = QgsTextFormat()
    text_format.setFont(QFont("Arial", 8))
    text_format.setSize(8)
    text_format.setColor(QColor(0, 0, 0))  # Black text
    
    label_settings.setFormat(text_format)
    
    # Enable labels
    label_settings.enabled = True
    
    # Apply labels to layer
    labeling = QgsVectorLayerSimpleLabeling(label_settings)
    layer.setLabelsEnabled(True)
    layer.setLabeling(labeling)
    
    print("✅ Labels added")

def setup_map_canvas(layer):
    """Set up the map canvas extent and CRS."""
    print("🗺️  Setting up map canvas...")
    
    # Get the project
    project = QgsProject.instance()
    
    # Set project CRS to WGS84
    crs = QgsCoordinateReferenceSystem("EPSG:4326")
    project.setCrs(crs)
    
    # Zoom to layer extent
    extent = layer.extent()
    project.viewSettings().setDefaultViewExtent(extent)
    
    print("✅ Map canvas configured")

def create_layout(layer):
    """Create a print layout with the map."""
    print("📄 Creating print layout...")
    
    try:
        project = QgsProject.instance()
        layout_manager = project.layoutManager()
        
        # Create new layout
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.setName("Arkansas Counties Map")
        
        # Add layout to manager
        layout_manager.addLayout(layout)
        
        # Add map item to layout
        map_item = QgsLayoutItemMap(layout)
        map_item.attemptSetSceneRect(QgsRectangle(20, 20, 200, 150))
        map_item.setExtent(layer.extent())
        
        # Add map item to layout
        layout.addLayoutItem(map_item)
        
        print("✅ Print layout created")
        
    except Exception as e:
        print(f"⚠️  Layout creation failed: {e}")

def save_project():
    """Save the QGIS project."""
    print("💾 Saving QGIS project...")
    
    project = QgsProject.instance()
    
    # Set project title
    project.setTitle("Arkansas Counties Analysis")
    
    # Save the project
    success = project.write(str(PROJECT_PATH))
    
    if success:
        print(f"✅ Project saved: {PROJECT_PATH}")
        return True
    else:
        print(f"❌ Failed to save project")
        return False

def cleanup_qgis(qgs):
    """Clean up QGIS application."""
    print("🧹 Cleaning up...")
    qgs.exitQgis()
    print("✅ QGIS cleanup complete")

def main():
    """Main execution function."""
    print("🏛️  Creating Arkansas Counties QGIS Project")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Initialize QGIS
    qgs = initialize_qgis()
    
    try:
        # Load data
        layer = load_arkansas_counties()
        if not layer:
            sys.exit(1)
        
        # Add layer to project
        project = QgsProject.instance()
        project.addMapLayer(layer)
        
        # Style the layer
        style_counties_layer(layer)
        
        # Setup map canvas
        setup_map_canvas(layer)
        
        # Create layout
        create_layout(layer)
        
        # Save project
        if save_project():
            print(f"\n🎉 QGIS project created successfully!")
            print(f"📁 Project file: {PROJECT_PATH}")
            print(f"")
            print(f"To open the project:")
            print(f"1. Open QGIS")
            print(f"2. File → Open Project")
            print(f"3. Select: {PROJECT_PATH}")
            print(f"")
            print(f"Or double-click the .qgz file to open directly in QGIS")
        else:
            print(f"❌ Project creation failed")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Always cleanup
        cleanup_qgis(qgs)

def print_usage_info():
    """Print usage information."""
    print("Usage: python create_qgis_project.py")
    print("")
    print("This script creates a QGIS project with Arkansas counties data.")
    print("Make sure to run arkansas_counties_example.py first to download the data.")
    print("")
    print("Requirements:")
    print("- QGIS must be installed")
    print("- Run in QGIS Python environment or with QGIS Python path configured")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print_usage_info()
        sys.exit(0)
    
    main()
