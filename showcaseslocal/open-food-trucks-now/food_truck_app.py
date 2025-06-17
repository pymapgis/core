#!/usr/bin/env python3
"""
Open Food Trucks Now - Standalone FastAPI Web Application
Serves San Francisco live lunch location heat-map
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()

# Change to the script directory for consistent file access
os.chdir(SCRIPT_DIR)

# Initialize FastAPI app
app = FastAPI(
    title="Open Food Trucks Now",
    description="San Francisco live lunch location heat-map",
    version="1.0.0"
)

# Mount static files (will be done after startup)
static_dir = SCRIPT_DIR / "static"

@app.on_event("startup")
async def startup_event():
    """Run food truck worker on startup to ensure fresh data"""
    print("🚚 Starting Open Food Trucks Now...")
    
    # Mount static files after ensuring directory exists
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        print(f"✅ Static files mounted from {static_dir}")
    
    try:
        # Run the food truck worker to process latest data
        worker_path = SCRIPT_DIR / "truck_worker.py"
        result = subprocess.run([sys.executable, str(worker_path)], 
                              capture_output=True, text=True, timeout=30, cwd=str(SCRIPT_DIR))
        if result.returncode == 0:
            print("✅ Food truck data processing completed successfully")
        else:
            print(f"⚠️ Food truck worker completed with warnings: {result.stderr}")
    except Exception as e:
        print(f"❌ Error running food truck worker: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interactive map interface"""
    html_file = SCRIPT_DIR / "static" / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(), status_code=200)
    else:
        return HTMLResponse(content="<h1>Open Food Trucks Now</h1><p>Map interface not found</p>", status_code=404)

@app.get("/public/latest")
async def get_public_data():
    """Get latest food truck data (public endpoint)"""
    try:
        data_file = SCRIPT_DIR / "food_trucks_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Food truck data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Add metadata
        response = {
            "status": "success",
            "data": data,
            "last_updated": datetime.now().isoformat() + "Z",
            "summary": data.get("summary", {}),
            "truck_count": data.get("summary", {}).get("total_trucks", 0),
            "neighborhood_count": data.get("summary", {}).get("total_neighborhoods", 0),
            "active_neighborhoods": data.get("summary", {}).get("neighborhoods_with_trucks", 0)
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading food truck data: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        data_file = SCRIPT_DIR / "food_trucks_latest.json"
        data_available = data_file.exists()
        
        if data_available:
            with open(data_file, "r") as f:
                data = json.load(f)
            total_trucks = data.get("summary", {}).get("total_trucks", 0)
            total_neighborhoods = data.get("summary", {}).get("total_neighborhoods", 0)
            active_neighborhoods = data.get("summary", {}).get("neighborhoods_with_trucks", 0)
        else:
            total_trucks = 0
            total_neighborhoods = 0
            active_neighborhoods = 0
        
        return {
            "status": "healthy",
            "service": "Open Food Trucks Now",
            "data_available": data_available,
            "total_trucks": total_trucks,
            "total_neighborhoods": total_neighborhoods,
            "active_neighborhoods": active_neighborhoods,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Open Food Trucks Now",
            "error": str(e),
            "last_updated": datetime.now().isoformat() + "Z"
        }

@app.get("/neighborhoods")
async def get_neighborhoods():
    """Get SF neighborhoods with food truck density"""
    try:
        data_file = SCRIPT_DIR / "food_trucks_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Food truck data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        neighborhoods = data.get("neighborhoods", {})
        
        return {
            "status": "success",
            "neighborhoods": neighborhoods,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading neighborhood data: {str(e)}")

@app.get("/trucks")
async def get_food_trucks():
    """Get current food truck locations"""
    try:
        data_file = SCRIPT_DIR / "food_trucks_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Food truck data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        food_trucks = data.get("food_trucks", {})
        
        return {
            "status": "success",
            "food_trucks": food_trucks,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading food truck data: {str(e)}")

if __name__ == "__main__":
    print("🚚 Starting Open Food Trucks Now API server...")
    print("📍 View at: http://localhost:8000")
    print("🗺️  Map interface: http://localhost:8000/")
    print("📊 Public data: http://localhost:8000/public/latest")
    print("🏙️  Neighborhoods: http://localhost:8000/neighborhoods")
    print("🚚 Food trucks: http://localhost:8000/trucks")
    print("❤️  Health check: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
