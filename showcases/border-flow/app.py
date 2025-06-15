"""
FastAPI Web Application for Border Flow Now

A 15-line FastAPI app that serves:
- GET / - Interactive MapLibre viewer
- GET /public/tiles/{z}/{x}/{y}.pbf - Vector tiles (anonymous)
- GET /internal/json - Full GeoJSON feed (JWT-protected)
- GET /health - Health check endpoint

Real-time CBP truck wait map powered by PyMapGIS.
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import Response, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from pathlib import Path
from typing import Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Border Flow Now",
    description="Real-time truck wait times at US border crossings - supply chain logistics intelligence",
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
    """Load the latest border wait time data."""
    global latest_data, last_updated

    try:
        if Path("bwt_latest.geojson").exists():
            with open("bwt_latest.geojson", "r") as f:
                latest_data = json.load(f)
            last_updated = Path("bwt_latest.geojson").stat().st_mtime
            logger.info("Loaded latest border wait time data")
        else:
            logger.warning("No bwt_latest.geojson file found")
            latest_data = {"type": "FeatureCollection", "features": []}
    except Exception as e:
        logger.error(f"Error loading border data: {e}")
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
        raise HTTPException(
            status_code=401, 
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    
    # Demo token validation (replace with real JWT validation)
    if token != "demo-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"user": "demo_user", "token": token}


@app.get("/public/tiles/{z}/{x}/{y}.pbf")
async def get_public_tiles(z: int, x: int, y: int):
    """
    Serve public vector tiles for anonymous access - border wait times.
    """
    tile_path = Path(f"tiles/bwt/{z}/{x}/{y}.mvt")

    if not tile_path.exists():
        # Return empty tile if not found
        return Response(content=b"", media_type="application/vnd.mapbox-vector-tile")

    try:
        with open(tile_path, "rb") as f:
            content = f.read()
        return Response(content=content, media_type="application/vnd.mapbox-vector-tile")
    except Exception as e:
        logger.error(f"Error serving border wait tile {z}/{x}/{y}: {e}")
        raise HTTPException(status_code=500, detail="Error serving tile")


@app.get("/internal/json")
async def get_latest_border_data(user=Depends(jwt_verify)):
    """
    Get latest border wait time data (JWT protected) - full GeoJSON feed.
    """
    if latest_data is None:
        load_latest_data()

    return {
        "data": latest_data,
        "last_updated": last_updated,
        "user": user["user"],
        "crossings_count": len(latest_data.get("features", [])),
        "service": "border-flow-now"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring border flow service.
    """
    # Check if data files exist
    data_status = "ok" if Path("bwt_latest.geojson").exists() else "no_data"
    tiles_status = "ok" if Path("tiles/bwt").exists() else "no_tiles"
    png_status = "ok" if Path("bwt.png").exists() else "no_png"

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "border-flow-now",
        "description": "Real-time US border crossing wait times",
        "checks": {
            "data_file": data_status,
            "tiles": tiles_status,
            "overview_png": png_status,
            "crossings_count": len(latest_data.get("features", [])) if latest_data else 0
        }
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serve the main interactive viewer.
    """
    # Serve the static HTML file
    static_file = Path("static/index.html")
    if static_file.exists():
        return FileResponse(static_file)
    else:
        # Fallback minimal HTML if static file missing
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Border Flow Now</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <h1>Border Flow Now</h1>
            <p>Interactive map viewer not found. Please check static/index.html</p>
            <ul>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/static/overview.png">Static Overview</a></li>
            </ul>
        </body>
        </html>
        """)


@app.get("/static/{filename}")
async def get_static_file(filename: str):
    """
    Serve static files (border wait PNG overview, etc.).
    """
    # Check in static directory first
    static_path = Path(f"static/{filename}")
    if static_path.exists():
        return FileResponse(static_path)

    # Check in root directory for generated files (bwt.png, etc.)
    root_path = Path(filename)
    if root_path.exists():
        return FileResponse(root_path)

    raise HTTPException(status_code=404, detail="File not found")


# ─── static MapLibre viewer (mount static files)
if Path("static").exists():
    app.mount("/", StaticFiles(directory="static", html=True), name="static")


# Mount static files directory if it exists
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
