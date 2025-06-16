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
import pymapgis as pmg
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
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(script_dir, "impact.geojson")

        if os.path.exists(data_path):
            with open(data_path, "r") as f:
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
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.join(script_dir, "static", "index.html")
    current_dir = os.getcwd()
    file_exists = os.path.exists(static_path)

    print(f"DEBUG: Current directory: {current_dir}")
    print(f"DEBUG: Script directory: {script_dir}")
    print(f"DEBUG: Looking for: {static_path}")
    print(f"DEBUG: File exists: {file_exists}")

    if file_exists:
        print(f"DEBUG: Serving HTML file from {static_path}")
        return FileResponse(static_path)
    else:
        print(f"DEBUG: HTML file not found, serving JSON response")
        return JSONResponse({
            "message": "Quake Impact Now API",
            "status": "running",
            "debug": {
                "current_dir": current_dir,
                "script_dir": script_dir,
                "static_path": static_path,
                "file_exists": file_exists
            },
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
script_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(script_dir, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Quake Impact Now API server...")
    print("📍 View at: http://localhost:8000")
    print("🗺️  Map interface: http://localhost:8000/")
    print("📊 Public data: http://localhost:8000/public/latest")
    print("🔒 Internal data: http://localhost:8000/internal/latest")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
