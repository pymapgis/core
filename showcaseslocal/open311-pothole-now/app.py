#!/usr/bin/env python3
"""
Open311 Pothole Now - FastAPI Web Application
Serves San Francisco civic issues tracking
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
    title="Open311 Pothole Now",
    description="San Francisco civic issues tracking",
    version="1.0.0"
)

# Mount static files (will be done after startup)
static_dir = SCRIPT_DIR / "static"

@app.on_event("startup")
async def startup_event():
    """Run pothole worker on startup to ensure fresh data"""
    print("🕳️ Starting Open311 Pothole Now...")
    
    # Mount static files after ensuring directory exists
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        print(f"✅ Static files mounted from {static_dir}")
    
    try:
        # Run the pothole worker to process latest data
        worker_path = SCRIPT_DIR / "pothole_worker.py"
        result = subprocess.run([sys.executable, str(worker_path)], 
                              capture_output=True, text=True, timeout=30, cwd=str(SCRIPT_DIR))
        if result.returncode == 0:
            print("✅ Civic issues data processing completed successfully")
        else:
            print(f"⚠️ Pothole worker completed with warnings: {result.stderr}")
    except Exception as e:
        print(f"❌ Error running pothole worker: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interactive map interface"""
    html_file = SCRIPT_DIR / "static" / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(), status_code=200)
    else:
        return HTMLResponse(content="<h1>Open311 Pothole Now</h1><p>Map interface not found</p>", status_code=404)

@app.get("/public/latest")
async def get_public_data():
    """Get latest civic issues data (public endpoint)"""
    try:
        data_file = SCRIPT_DIR / "open311_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Civic issues data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Add metadata
        response = {
            "status": "success",
            "data": data,
            "last_updated": datetime.now().isoformat() + "Z",
            "summary": data.get("summary", {}),
            "total_issues": data.get("summary", {}).get("total_issues", 0),
            "open_issues": data.get("summary", {}).get("open_issues", 0),
            "high_priority": data.get("summary", {}).get("high_priority", 0)
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading civic issues data: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        data_file = SCRIPT_DIR / "open311_latest.json"
        data_available = data_file.exists()
        
        if data_available:
            with open(data_file, "r") as f:
                data = json.load(f)
            total_issues = data.get("summary", {}).get("total_issues", 0)
            open_issues = data.get("summary", {}).get("open_issues", 0)
            high_priority = data.get("summary", {}).get("high_priority", 0)
        else:
            total_issues = 0
            open_issues = 0
            high_priority = 0
        
        return {
            "status": "healthy",
            "service": "Open311 Pothole Now",
            "data_available": data_available,
            "total_issues": total_issues,
            "open_issues": open_issues,
            "high_priority": high_priority,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Open311 Pothole Now",
            "error": str(e),
            "last_updated": datetime.now().isoformat() + "Z"
        }

@app.get("/issues")
async def get_street_defects():
    """Get current street defects and civic issues"""
    try:
        data_file = SCRIPT_DIR / "open311_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Civic issues data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        street_defects = data.get("street_defects", {})
        
        return {
            "status": "success",
            "street_defects": street_defects,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading street defects data: {str(e)}")

if __name__ == "__main__":
    print("🕳️ Starting Open311 Pothole Now API server...")
    print("📍 View at: http://localhost:8000")
    print("🗺️  Map interface: http://localhost:8000/")
    print("📊 Public data: http://localhost:8000/public/latest")
    print("🚧 Street issues: http://localhost:8000/issues")
    print("❤️  Health check: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
