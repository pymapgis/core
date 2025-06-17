#!/usr/bin/env python3
"""
Ship Traffic Now - FastAPI Web Application
Serves real-time maritime vessel tracking with interactive map interface
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
    title="Ship Traffic Now",
    description="Real-time maritime vessel tracking and port congestion analysis",
    version="1.0.0"
)

# Mount static files (will be done after startup)
static_dir = SCRIPT_DIR / "static"

@app.on_event("startup")
async def startup_event():
    """Run ship worker on startup to ensure fresh data"""
    print("🚀 Starting Ship Traffic Now...")
    
    # Mount static files after ensuring directory exists
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        print(f"✅ Static files mounted from {static_dir}")
    
    try:
        # Run the ship worker to process latest data
        worker_path = SCRIPT_DIR / "ship_worker.py"
        result = subprocess.run([sys.executable, str(worker_path)], 
                              capture_output=True, text=True, timeout=30, cwd=str(SCRIPT_DIR))
        if result.returncode == 0:
            print("✅ Ship traffic data processing completed successfully")
        else:
            print(f"⚠️ Ship worker completed with warnings: {result.stderr}")
    except Exception as e:
        print(f"❌ Error running ship worker: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interactive map interface"""
    html_file = SCRIPT_DIR / "static" / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(), status_code=200)
    else:
        return HTMLResponse(content="<h1>Ship Traffic Now</h1><p>Map interface not found</p>", status_code=404)

@app.get("/public/latest")
async def get_public_data():
    """Get latest ship traffic data (public endpoint)"""
    try:
        data_file = SCRIPT_DIR / "ship_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Ship traffic data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Add metadata
        response = {
            "status": "success",
            "data": data,
            "last_updated": datetime.now().isoformat() + "Z",
            "summary": data.get("summary", {}),
            "vessel_count": data.get("summary", {}).get("total_vessels", 0),
            "port_count": data.get("summary", {}).get("total_ports", 0)
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading ship traffic data: {str(e)}")

@app.get("/internal/latest")
async def get_internal_data():
    """Get full analyst data with metadata (protected endpoint)"""
    try:
        # For demo purposes, this returns the same data as public
        # In production, this would include additional analyst fields
        data_file = SCRIPT_DIR / "ship_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Ship traffic data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Enhanced response with analyst metadata
        response = {
            "status": "success",
            "data": data,
            "metadata": {
                "last_updated": datetime.now().isoformat() + "Z",
                "total_vessels": data.get("summary", {}).get("total_vessels", 0),
                "total_ports": data.get("summary", {}).get("total_ports", 0),
                "data_source": "AIS Maritime Traffic",
                "processing_version": "1.0.0",
                "coverage": "Major US Ports",
                "update_frequency": "2 minutes",
                "summary": data.get("summary", {})
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading ship traffic data: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        data_file = SCRIPT_DIR / "ship_latest.json"
        data_available = data_file.exists()
        
        if data_available:
            with open(data_file, "r") as f:
                data = json.load(f)
            total_vessels = data.get("summary", {}).get("total_vessels", 0)
            total_ports = data.get("summary", {}).get("total_ports", 0)
        else:
            total_vessels = 0
            total_ports = 0
        
        return {
            "status": "healthy",
            "service": "Ship Traffic Now",
            "data_available": data_available,
            "total_vessels": total_vessels,
            "total_ports": total_ports,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Ship Traffic Now",
            "error": str(e),
            "last_updated": datetime.now().isoformat() + "Z"
        }

def calculate_summary(data):
    """Calculate summary statistics from ship traffic data"""
    try:
        vessels = data.get("vessels", {}).get("features", [])
        ports = data.get("ports", {}).get("features", [])
        
        if not vessels or not ports:
            return {"total_vessels": 0, "total_ports": 0, "avg_congestion": 0, "busiest_port": "N/A"}
        
        # Calculate congestion statistics
        congestion_scores = []
        for port in ports:
            props = port.get("properties", {})
            score = props.get("congestion_score", 0)
            congestion_scores.append(score)
        
        # Find busiest port
        busiest_port = "N/A"
        max_congestion = 0
        for port in ports:
            props = port.get("properties", {})
            score = props.get("congestion_score", 0)
            if score > max_congestion:
                max_congestion = score
                busiest_port = props.get("name", "Unknown")
        
        return {
            "total_vessels": len(vessels),
            "total_ports": len(ports),
            "avg_congestion": round(sum(congestion_scores) / len(congestion_scores), 2) if congestion_scores else 0,
            "busiest_port": busiest_port
        }
    
    except Exception:
        return {"total_vessels": 0, "total_ports": 0, "avg_congestion": 0, "busiest_port": "N/A"}

if __name__ == "__main__":
    print("🚢 Starting Ship Traffic Now API server...")
    print("📍 View at: http://localhost:8000")
    print("🗺️  Map interface: http://localhost:8000/")
    print("📊 Public data: http://localhost:8000/public/latest")
    print("🔒 Internal data: http://localhost:8000/internal/latest")
    print("❤️  Health check: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
