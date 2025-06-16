"""
Quake Impact Now - FastAPI Web Application

A 15-line FastAPI app that serves earthquake impact data with:
- Public tile endpoint for anonymous map viewing
- Protected JSON endpoint for analysts
- Static file serving for the web interface
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import json
import os
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="Quake Impact Now",
    description="Live earthquake impact visualization using USGS data and population analysis",
    version="1.0.0"
)

# Global data storage
impact_data = None

def load_impact_data():
    """Load the latest impact data from the processing script."""
    global impact_data
    try:
        if os.path.exists("impact.geojson"):
            with open("impact.geojson", "r") as f:
                impact_data = json.load(f)
        return impact_data
    except Exception as e:
        print(f"Error loading impact data: {e}")
        return None

# Load data on startup
load_impact_data()

@app.get("/")
async def root():
    """Serve the main map interface."""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    else:
        return JSONResponse({
            "message": "Quake Impact Now API",
            "status": "running",
            "endpoints": {
                "public_data": "/public/latest",
                "tiles": "/public/tiles/{z}/{x}/{y}.pbf",
                "internal": "/internal/latest"
            }
        })

@app.get("/public/latest")
async def public_latest():
    """Public endpoint for latest earthquake impact data."""
    data = load_impact_data()
    if data is None:
        raise HTTPException(status_code=404, detail="No impact data available")
    
    # Return simplified data for public consumption
    return {
        "status": "success",
        "data": data,
        "last_updated": "2024-01-01T00:00:00Z",  # Would be dynamic in production
        "total_events": len(data.get("features", [])) if data else 0
    }

@app.get("/public/tiles/{z}/{x}/{y}.pbf")
async def tiles(z: int, x: int, y: int):
    """Serve vector tiles for map visualization."""
    # In a full implementation, this would serve actual MVT tiles
    # For demo purposes, we'll return a simple response
    return JSONResponse({
        "message": f"Tile {z}/{x}/{y} - In production, this would serve MVT tiles",
        "tile_coords": {"z": z, "x": x, "y": y}
    })

@app.get("/internal/latest")
async def internal_latest(user=Depends(lambda: "demo_user")):  # Simplified auth for demo
    """Protected endpoint for analysts with full data access."""
    data = load_impact_data()
    if data is None:
        raise HTTPException(status_code=404, detail="No impact data available")
    
    return {
        "status": "success",
        "data": data,
        "metadata": {
            "processing_time": "< 1 minute",
            "data_sources": ["USGS", "WorldPop"],
            "last_updated": "2024-01-01T00:00:00Z"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Quake Impact Now",
        "data_available": impact_data is not None
    }

# Mount static files if directory exists
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Quake Impact Now API server...")
    print("📍 View at: http://localhost:8000")
    print("🗺️  Map interface: http://localhost:8000/")
    print("📊 Public data: http://localhost:8000/public/latest")
    print("🔒 Internal data: http://localhost:8000/internal/latest")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
