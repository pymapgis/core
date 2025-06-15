# ---
# title: {{DEMO_TITLE}}
# feed: {{DATA_URL}}
# category: {{CATEGORY}}
# license: CC0
# ---

"""
{{DEMO_TITLE}} - PyMapGIS Showcase Demo

{{DESCRIPTION}}

Data Source: {{DATA_URL}}
Update Frequency: {{UPDATE_FREQUENCY}}
Geographic Coverage: {{COVERAGE}}
"""

import pymapgis as pmg
import pandas as pd
import asyncio
import math
import datetime as dt
from pathlib import Path
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data sources (100% open, no API keys required)
DATA_URL = "{{DATA_URL}}"
BACKUP_DATA_URL = "{{BACKUP_DATA_URL}}"  # Optional fallback source

# Processing parameters
BUFFER_DISTANCE = 10000  # 10km in meters (adjust as needed)
OUTPUT_LAYER_NAME = "{{LAYER_NAME}}"


def create_test_data():
    """Create test data for demo purposes when live data unavailable."""
    import geopandas as gpd
    from shapely.geometry import Point
    
    # Create realistic test data for your demo
    test_data = {
        'id': ['test_001', 'test_002', 'test_003', 'test_004', 'test_005'],
        'name': ['Sample A', 'Sample B', 'Sample C', 'Sample D', 'Sample E'],
        'value': [1.2, 2.5, 0.8, 3.1, 1.9],  # Your metric values
        'geometry': [
            Point(-118.2437, 34.0522),  # Los Angeles
            Point(-122.4194, 37.7749),  # San Francisco  
            Point(-74.0060, 40.7128),   # New York
            Point(2.3522, 48.8566),     # Paris
            Point(139.6917, 35.6895)    # Tokyo
        ]
    }
    
    gdf = gpd.GeoDataFrame(test_data, crs="EPSG:4326")
    logger.info(f"Created {len(gdf)} test features for demo")
    return gdf


def calculate_score(data):
    """
    Calculate your custom score/metric for visualization.
    
    Args:
        data: GeoDataFrame with your features
        
    Returns:
        GeoDataFrame with added 'score' column
    """
    # Example scoring logic - replace with your domain-specific calculation
    # This could be risk assessment, impact calculation, priority scoring, etc.
    
    data['score'] = data['value'] * 10  # Simple example
    
    # More complex example:
    # data['score'] = np.log10(data['population']) * data['magnitude']
    # data['score'] = data['risk_factor'] * data['exposure'] * data['vulnerability']
    
    logger.info(f"Calculated scores (range: {data['score'].min():.1f} to {data['score'].max():.1f})")
    return data


async def main():
    """
    Main processing function - keep this concise and focused!
    
    The goal is to demonstrate PyMapGIS capabilities in ~40 lines:
    1. Data ingestion from public sources
    2. Geospatial processing (buffers, joins, analysis)
    3. Multi-format export (GeoJSON, MVT, PNG)
    """
    logger.info(f"Starting {{DEMO_TITLE}} processing...")
    
    # 1. Read data from public source
    logger.info("Fetching data from public source...")
    try:
        data = pmg.read(DATA_URL)
        logger.info(f"Successfully fetched {len(data)} features")
        
        if len(data) == 0:
            logger.warning("No data found, creating test data")
            data = create_test_data()
            
    except Exception as e:
        logger.warning(f"Could not fetch live data ({e}), using test data for demo")
        data = create_test_data()
    
    # 2. Geospatial processing with PyMapGIS
    logger.info("Processing geospatial data...")
    
    # Example: Buffer analysis (adjust based on your use case)
    if BUFFER_DISTANCE > 0:
        logger.info(f"Creating {BUFFER_DISTANCE/1000:.0f}km buffers...")
        data_proj = data.to_crs("EPSG:3857")  # Project for accurate buffering
        data_proj['geometry'] = data_proj.geometry.buffer(BUFFER_DISTANCE)
        data = data_proj.to_crs("EPSG:4326")  # Back to WGS84 for web display
    
    # Example: Async processing (if you need raster analysis, etc.)
    # gp = pmg.AsyncGeoProcessor(max_workers=4)
    # try:
    #     results = await gp.some_analysis(data)
    #     data['analysis_result'] = results
    # finally:
    #     await gp.close()
    
    # 3. Calculate your domain-specific score/metric
    logger.info("Calculating scores...")
    data = calculate_score(data)
    
    # 4. Create output directory
    output_dir = Path("tiles")
    output_dir.mkdir(exist_ok=True)
    
    # 5. Export to multiple formats for web consumption
    logger.info("Exporting results...")
    
    try:
        # Vector tiles for interactive web maps
        data.pmg.to_mvt(
            f"tiles/{OUTPUT_LAYER_NAME}/{{z}}/{{x}}/{{y}}.mvt",
            layer=OUTPUT_LAYER_NAME,
            fields=["name", "value", "score"]  # Adjust field list
        )
        logger.info(f"Vector tiles exported to tiles/{OUTPUT_LAYER_NAME}/")
    except Exception as e:
        logger.error(f"Vector tile export failed: {e}")
    
    # GeoJSON for full data access
    data.to_file("output.geojson", driver="GeoJSON")
    logger.info("GeoJSON exported to output.geojson")
    
    # Static PNG for overview/sharing
    try:
        data.pmg_plot.save_png(
            "overview.png",
            column="score",
            cmap="viridis",  # Adjust colormap as needed
            title=f"{{DEMO_TITLE}} - {dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC",
            dpi=150
        )
        logger.info("Static overview map saved as overview.png")
    except Exception as e:
        logger.error(f"Static map export failed: {e}")
    
    # 6. Summary statistics
    logger.info(f"✅ {dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC - Processed {len(data)} features")
    logger.info(f"📊 Score range: {data['score'].min():.1f} to {data['score'].max():.1f}")
    
    # Print top features for interest
    if len(data) > 0:
        top_features = data.nlargest(5, 'score')[['name', 'value', 'score']]
        logger.info("🔥 Top 5 features by score:")
        for idx, row in top_features.iterrows():
            logger.info(f"   {row['name']} - Value: {row['value']:.1f} - Score: {row['score']:.1f}")


if __name__ == "__main__":
    asyncio.run(main())
