#!/usr/bin/env python3
"""
Transit Crowding Now - FastAPI Web Application
Serves NYC subway real-time crowding analysis
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
    title="Transit Crowding Now",
    description="NYC subway real-time crowding analysis",
    version="1.0.0"
)

# Mount static files (will be done after startup)
static_dir = SCRIPT_DIR / "static"

@app.on_event("startup")
async def startup_event():
    """Run transit worker on startup to ensure fresh data"""
    print("🚇 Starting Transit Crowding Now...")
    
    # Mount static files after ensuring directory exists
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        print(f"✅ Static files mounted from {static_dir}")
    
    try:
        # Run the transit worker to process latest data
        worker_path = SCRIPT_DIR / "transit_worker.py"
        result = subprocess.run([sys.executable, str(worker_path)], 
                              capture_output=True, text=True, timeout=30, cwd=str(SCRIPT_DIR))
        if result.returncode == 0:
            print("✅ Transit crowding data processing completed successfully")
        else:
            print(f"⚠️ Transit worker completed with warnings: {result.stderr}")
    except Exception as e:
        print(f"❌ Error running transit worker: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interactive map interface"""
    html_file = SCRIPT_DIR / "static" / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(), status_code=200)
    else:
        return HTMLResponse(content="<h1>Transit Crowding Now</h1><p>Map interface not found</p>", status_code=404)

@app.get("/public/latest")
async def get_public_data():
    """Get latest transit crowding data (public endpoint)"""
    try:
        data_file = SCRIPT_DIR / "transit_crowding_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Transit crowding data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Add metadata
        response = {
            "status": "success",
            "data": data,
            "last_updated": datetime.now().isoformat() + "Z",
            "summary": data.get("summary", {}),
            "total_routes": data.get("summary", {}).get("total_routes", 0),
            "crowded_routes": data.get("summary", {}).get("crowded_routes", 0),
            "avg_crowd_score": data.get("summary", {}).get("avg_crowd_score", 0)
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading transit crowding data: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        data_file = SCRIPT_DIR / "transit_crowding_latest.json"
        data_available = data_file.exists()
        
        if data_available:
            with open(data_file, "r") as f:
                data = json.load(f)
            total_routes = data.get("summary", {}).get("total_routes", 0)
            crowded_routes = data.get("summary", {}).get("crowded_routes", 0)
            avg_crowd_score = data.get("summary", {}).get("avg_crowd_score", 0)
        else:
            total_routes = 0
            crowded_routes = 0
            avg_crowd_score = 0
        
        return {
            "status": "healthy",
            "service": "Transit Crowding Now",
            "data_available": data_available,
            "total_routes": total_routes,
            "crowded_routes": crowded_routes,
            "avg_crowd_score": avg_crowd_score,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Transit Crowding Now",
            "error": str(e),
            "last_updated": datetime.now().isoformat() + "Z"
        }

@app.get("/routes")
async def get_subway_routes():
    """Get current subway routes with crowding data"""
    try:
        data_file = SCRIPT_DIR / "transit_crowding_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Transit crowding data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        subway_routes = data.get("subway_routes", {})
        
        return {
            "status": "success",
            "subway_routes": subway_routes,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading subway routes data: {str(e)}")

@app.get("/alerts")
async def get_transit_alerts():
    """Get current transit alerts"""
    try:
        data_file = SCRIPT_DIR / "transit_crowding_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Transit crowding data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        alerts = data.get("alerts", [])
        
        return {
            "status": "success",
            "alerts": alerts,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading transit alerts data: {str(e)}")

if __name__ == "__main__":
    print("🚇 Starting Transit Crowding Now API server...")
    print("📍 View at: http://localhost:8000")
    print("🗺️  Map interface: http://localhost:8000/")
    print("📊 Public data: http://localhost:8000/public/latest")
    print("🚇 Subway routes: http://localhost:8000/routes")
    print("🚨 Transit alerts: http://localhost:8000/alerts")
    print("❤️  Health check: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
