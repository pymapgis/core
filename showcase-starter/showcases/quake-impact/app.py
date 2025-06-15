"""
FastAPI Web Application for Quake Impact Now

Serves:
- GET /public/tiles/{z}/{x}/{y}.pbf - Anonymous map layer (vector tiles)
- GET /internal/latest - JWT-protected full GeoJSON for analysts
- GET / - Interactive web viewer
- GET /health - Health check endpoint
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import Response, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pymapgis as pmg
import json
import os
from pathlib import Path
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Quake Impact Now",
    description="Live earthquake impact assessment using PyMapGIS",
    version="1.0.0"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data storage
latest_data = None
last_updated = None


def load_latest_data():
    """Load the latest earthquake impact data."""
    global latest_data, last_updated
    
    try:
        if Path("impact.geojson").exists():
            with open("impact.geojson", "r") as f:
                latest_data = json.load(f)
            last_updated = Path("impact.geojson").stat().st_mtime
            logger.info("Loaded latest earthquake impact data")
        else:
            logger.warning("No impact.geojson file found")
            latest_data = {"type": "FeatureCollection", "features": []}
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        latest_data = {"type": "FeatureCollection", "features": []}


# Load data on startup
load_latest_data()


# Simple JWT verification (demo purposes - use proper JWT in production)
def jwt_verify(request: Request):
    """
    Simple JWT verification for demo purposes.
    In production, use proper JWT validation with secret keys.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    
    # Demo token validation (replace with real JWT validation)
    if token != "demo-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"user": "demo_user", "token": token}


@app.get("/public/tiles/{z}/{x}/{y}.pbf")
async def get_public_tiles(z: int, x: int, y: int):
    """
    Serve public vector tiles for anonymous access.
    """
    tile_path = Path(f"tiles/impact/{z}/{x}/{y}.mvt")
    
    if not tile_path.exists():
        # Return empty tile if not found
        return Response(content=b"", media_type="application/vnd.mapbox-vector-tile")
    
    try:
        with open(tile_path, "rb") as f:
            content = f.read()
        return Response(content=content, media_type="application/vnd.mapbox-vector-tile")
    except Exception as e:
        logger.error(f"Error serving tile {z}/{x}/{y}: {e}")
        raise HTTPException(status_code=500, detail="Error serving tile")


@app.get("/internal/latest")
async def get_latest_data(user=Depends(jwt_verify)):
    """
    Get latest earthquake impact data (JWT protected).
    """
    if latest_data is None:
        load_latest_data()
    
    return {
        "data": latest_data,
        "last_updated": last_updated,
        "user": user["user"],
        "features_count": len(latest_data.get("features", []))
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    from datetime import datetime
    
    # Check if data files exist
    data_status = "ok" if Path("impact.geojson").exists() else "no_data"
    tiles_status = "ok" if Path("tiles/impact").exists() else "no_tiles"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "quake-impact-now",
        "checks": {
            "data_file": data_status,
            "tiles": tiles_status,
            "features_count": len(latest_data.get("features", [])) if latest_data else 0
        }
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serve the main interactive viewer.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>Quake Impact Now</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://unpkg.com/maplibre-gl@3.6.0/dist/maplibre-gl.js"></script>
        <link href="https://unpkg.com/maplibre-gl@3.6.0/dist/maplibre-gl.css" rel="stylesheet" />
        <style>
            body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
            #map { position: absolute; top: 0; bottom: 0; width: 100%; }
            .info-panel {
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(255, 255, 255, 0.9);
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                max-width: 300px;
                z-index: 1000;
            }
            .legend {
                position: absolute;
                bottom: 30px;
                right: 10px;
                background: rgba(255, 255, 255, 0.9);
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                z-index: 1000;
            }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <div class="info-panel">
            <h3>🌍 Quake Impact Now</h3>
            <p>Live earthquake impact assessment powered by PyMapGIS</p>
            <p><strong>Data:</strong> USGS (last 24h) + WorldPop 2020</p>
            <p><strong>Impact Score:</strong> log₁₀(population) × magnitude</p>
            <p><em>Click on earthquakes for details</em></p>
        </div>
        <div class="legend">
            <h4>Impact Scale</h4>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 15px; height: 15px; background: #00bfff; margin-right: 5px; border-radius: 50%;"></div>
                <span>Low (0-4)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 15px; height: 15px; background: #ffff00; margin-right: 5px; border-radius: 50%;"></div>
                <span>Medium (4-6)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 15px; height: 15px; background: #ff7e00; margin-right: 5px; border-radius: 50%;"></div>
                <span>High (6-8)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 15px; height: 15px; background: #ff0000; margin-right: 5px; border-radius: 50%;"></div>
                <span>Extreme (8+)</span>
            </div>
        </div>
        
        <script>
            const map = new maplibregl.Map({
                container: 'map',
                style: {
                    version: 8,
                    sources: {
                        'osm': {
                            type: 'raster',
                            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                            tileSize: 256,
                            attribution: '© OpenStreetMap contributors'
                        }
                    },
                    layers: [{
                        id: 'osm',
                        type: 'raster',
                        source: 'osm'
                    }]
                },
                center: [-120, 37],
                zoom: 3
            });

            map.addControl(new maplibregl.NavigationControl());

            map.on('load', () => {
                map.addSource('quakes', {
                    type: 'vector',
                    tiles: [window.location.origin + '/public/tiles/{z}/{x}/{y}.pbf'],
                    minzoom: 0,
                    maxzoom: 14
                });

                map.addLayer({
                    id: 'quake-circles',
                    type: 'circle',
                    source: 'quakes',
                    'source-layer': 'quake',
                    paint: {
                        'circle-radius': [
                            'interpolate',
                            ['linear'],
                            ['get', 'Impact'],
                            0, 3,
                            4, 8,
                            6, 15,
                            8, 25
                        ],
                        'circle-color': [
                            'interpolate',
                            ['linear'],
                            ['get', 'Impact'],
                            0, '#00bfff',
                            4, '#ffff00',
                            6, '#ff7e00',
                            8, '#ff0000'
                        ],
                        'circle-opacity': 0.8,
                        'circle-stroke-width': 1,
                        'circle-stroke-color': '#ffffff'
                    }
                });

                map.on('click', 'quake-circles', (e) => {
                    const props = e.features[0].properties;
                    new maplibregl.Popup()
                        .setLngLat(e.lngLat)
                        .setHTML(`
                            <h3>Magnitude ${props.mag}</h3>
                            <p><strong>Impact Score:</strong> ${parseFloat(props.Impact).toFixed(1)}</p>
                            <p><strong>Population (50km):</strong> ${parseInt(props.pop50k).toLocaleString()}</p>
                            <p><strong>Event ID:</strong> ${props.id}</p>
                        `)
                        .addTo(map);
                });

                map.on('mouseenter', 'quake-circles', () => {
                    map.getCanvas().style.cursor = 'pointer';
                });

                map.on('mouseleave', 'quake-circles', () => {
                    map.getCanvas().style.cursor = '';
                });
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/static/{filename}")
async def get_static_file(filename: str):
    """
    Serve static files (like the overview PNG).
    """
    file_path = Path(filename)
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
