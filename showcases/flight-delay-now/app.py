#!/usr/bin/env python3
"""
Flight Delay Now - FastAPI Web Application
Serves real-time airport delay data with interactive map interface
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
    title="Flight Delay Now",
    description="Real-time airport delay analysis and visualization",
    version="1.0.0"
)

# Mount static files (will be done after startup)
static_dir = SCRIPT_DIR / "static"

@app.on_event("startup")
async def startup_event():
    """Run flight worker on startup to ensure fresh data"""
    print("🚀 Starting Flight Delay Now...")

    # Mount static files after ensuring directory exists
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        print(f"✅ Static files mounted from {static_dir}")

    try:
        # Run the flight worker to process latest data
        worker_path = SCRIPT_DIR / "flight_worker.py"
        result = subprocess.run([sys.executable, str(worker_path)],
                              capture_output=True, text=True, timeout=30, cwd=str(SCRIPT_DIR))
        if result.returncode == 0:
            print("✅ Flight data processing completed successfully")
        else:
            print(f"⚠️ Flight worker completed with warnings: {result.stderr}")
    except Exception as e:
        print(f"❌ Error running flight worker: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interactive map interface"""
    html_file = SCRIPT_DIR / "static" / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(), status_code=200)
    else:
        return HTMLResponse(content="<h1>Flight Delay Now</h1><p>Map interface not found</p>", status_code=404)

@app.get("/public/latest")
async def get_public_data():
    """Get latest flight delay data (public endpoint)"""
    try:
        data_file = SCRIPT_DIR / "flight_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Flight data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Add metadata
        response = {
            "status": "success",
            "data": data,
            "last_updated": datetime.now().isoformat() + "Z",
            "total_airports": len(data.get("features", [])),
            "summary": calculate_summary(data)
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading flight data: {str(e)}")

@app.get("/internal/latest")
async def get_internal_data():
    """Get full analyst data with metadata (protected endpoint)"""
    try:
        # For demo purposes, this returns the same data as public
        # In production, this would include additional analyst fields
        data_file = SCRIPT_DIR / "flight_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Flight data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Enhanced response with analyst metadata
        response = {
            "status": "success",
            "data": data,
            "metadata": {
                "last_updated": datetime.now().isoformat() + "Z",
                "total_airports": len(data.get("features", [])),
                "data_source": "FAA OIS",
                "processing_version": "1.0.0",
                "summary": calculate_summary(data)
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading flight data: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        data_file = SCRIPT_DIR / "flight_latest.json"
        data_available = data_file.exists()
        
        if data_available:
            with open(data_file, "r") as f:
                data = json.load(f)
            total_airports = len(data.get("features", []))
        else:
            total_airports = 0
        
        return {
            "status": "healthy",
            "service": "Flight Delay Now",
            "data_available": data_available,
            "total_airports": total_airports,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Flight Delay Now",
            "error": str(e),
            "last_updated": datetime.now().isoformat() + "Z"
        }

def calculate_summary(data):
    """Calculate summary statistics from flight data"""
    try:
        features = data.get("features", [])
        if not features:
            return {"avg_delay": 0, "max_delay": 0, "delayed_airports": 0}
        
        delays = []
        delayed_count = 0
        
        for feature in features:
            props = feature.get("properties", {})
            delay = props.get("avg_delay", 0)
            delays.append(delay)
            if delay > 15:  # Consider 15+ minutes as delayed
                delayed_count += 1
        
        return {
            "avg_delay": round(sum(delays) / len(delays), 1) if delays else 0,
            "max_delay": max(delays) if delays else 0,
            "delayed_airports": delayed_count
        }
    
    except Exception:
        return {"avg_delay": 0, "max_delay": 0, "delayed_airports": 0}

if __name__ == "__main__":
    print("✈️ Starting Flight Delay Now API server...")
    print("📍 View at: http://localhost:8000")
    print("🗺️  Map interface: http://localhost:8000/")
    print("📊 Public data: http://localhost:8000/public/latest")
    print("🔒 Internal data: http://localhost:8000/internal/latest")
    print("❤️  Health check: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
