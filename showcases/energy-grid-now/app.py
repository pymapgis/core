#!/usr/bin/env python3
"""
Energy Grid Now - FastAPI Web Application
Serves real-time power grid monitoring and outage impact analysis
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
    title="Energy Grid Now",
    description="Real-time power grid monitoring and outage impact analysis",
    version="1.0.0"
)

# Mount static files (will be done after startup)
static_dir = SCRIPT_DIR / "static"

@app.on_event("startup")
async def startup_event():
    """Run energy worker on startup to ensure fresh data"""
    print("🚀 Starting Energy Grid Now...")
    
    # Mount static files after ensuring directory exists
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        print(f"✅ Static files mounted from {static_dir}")
    
    try:
        # Run the energy worker to process latest data
        worker_path = SCRIPT_DIR / "energy_worker.py"
        result = subprocess.run([sys.executable, str(worker_path)], 
                              capture_output=True, text=True, timeout=30, cwd=str(SCRIPT_DIR))
        if result.returncode == 0:
            print("✅ Energy grid data processing completed successfully")
        else:
            print(f"⚠️ Energy worker completed with warnings: {result.stderr}")
    except Exception as e:
        print(f"❌ Error running energy worker: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interactive map interface"""
    html_file = SCRIPT_DIR / "static" / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(), status_code=200)
    else:
        return HTMLResponse(content="<h1>Energy Grid Now</h1><p>Map interface not found</p>", status_code=404)

@app.get("/public/latest")
async def get_public_data():
    """Get latest energy grid data (public endpoint)"""
    try:
        data_file = SCRIPT_DIR / "energy_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Energy grid data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Add metadata
        response = {
            "status": "success",
            "data": data,
            "last_updated": datetime.now().isoformat() + "Z",
            "summary": data.get("summary", {}),
            "facility_count": data.get("summary", {}).get("total_facilities", 0),
            "total_capacity_mw": data.get("summary", {}).get("total_capacity_mw", 0),
            "critical_facilities": data.get("summary", {}).get("critical_facilities", 0)
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading energy grid data: {str(e)}")

@app.get("/internal/latest")
async def get_internal_data():
    """Get full analyst data with metadata (protected endpoint)"""
    try:
        # For demo purposes, this returns the same data as public
        # In production, this would include additional analyst fields
        data_file = SCRIPT_DIR / "energy_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Energy grid data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Enhanced response with analyst metadata
        response = {
            "status": "success",
            "data": data,
            "metadata": {
                "last_updated": datetime.now().isoformat() + "Z",
                "total_facilities": data.get("summary", {}).get("total_facilities", 0),
                "total_capacity_mw": data.get("summary", {}).get("total_capacity_mw", 0),
                "avg_resilience": data.get("summary", {}).get("avg_resilience", 0),
                "critical_facilities": data.get("summary", {}).get("critical_facilities", 0),
                "facilities_with_outages": data.get("summary", {}).get("facilities_with_outages", 0),
                "high_risk_facilities": data.get("summary", {}).get("high_risk_facilities", 0),
                "data_source": "EIA Energy Information Administration",
                "processing_version": "1.0.0",
                "coverage": "Major US Power Facilities",
                "update_frequency": "3 minutes",
                "resilience_factors": ["Capacity", "Outage Status", "Demand", "Facility Age"],
                "grid_regions": ["WECC", "ERCOT", "Eastern Interconnection"],
                "regional_health": data.get("regional_health", {}),
                "summary": data.get("summary", {})
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading energy grid data: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        data_file = SCRIPT_DIR / "energy_latest.json"
        data_available = data_file.exists()
        
        if data_available:
            with open(data_file, "r") as f:
                data = json.load(f)
            total_facilities = data.get("summary", {}).get("total_facilities", 0)
            total_capacity = data.get("summary", {}).get("total_capacity_mw", 0)
            critical_facilities = data.get("summary", {}).get("critical_facilities", 0)
        else:
            total_facilities = 0
            total_capacity = 0
            critical_facilities = 0
        
        return {
            "status": "healthy",
            "service": "Energy Grid Now",
            "data_available": data_available,
            "total_facilities": total_facilities,
            "total_capacity_mw": total_capacity,
            "critical_facilities": critical_facilities,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Energy Grid Now",
            "error": str(e),
            "last_updated": datetime.now().isoformat() + "Z"
        }

@app.get("/outages")
async def get_current_outages():
    """Get current power outages and grid issues"""
    try:
        data_file = SCRIPT_DIR / "energy_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Energy grid data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Extract facilities with outages or issues
        grid_features = data.get("grid", {}).get("features", [])
        outages = []
        
        for feature in grid_features:
            props = feature.get("properties", {})
            outage_status = props.get("outage_status", "Normal")
            resilience = props.get("resilience_score", 100)
            
            if outage_status != "Normal" or resilience < 50:  # Issues threshold
                outages.append({
                    "facility_name": props.get("facility_name", "Unknown"),
                    "outage_status": outage_status,
                    "resilience_score": resilience,
                    "capacity_mw": props.get("capacity_mw", 0),
                    "facility_type": props.get("facility_type", "Unknown"),
                    "economic_impact": props.get("economic_impact", 0),
                    "alert_level": props.get("alert_level", "Low"),
                    "coordinates": feature.get("geometry", {}).get("coordinates", [0, 0])
                })
        
        return {
            "status": "success",
            "outage_count": len(outages),
            "outages": sorted(outages, key=lambda x: x["resilience_score"]),
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading outage data: {str(e)}")

@app.get("/regional")
async def get_regional_health():
    """Get regional grid health analysis"""
    try:
        data_file = SCRIPT_DIR / "energy_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Energy grid data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        regional_health = data.get("regional_health", {})
        
        return {
            "status": "success",
            "regional_health": regional_health,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading regional data: {str(e)}")

def calculate_summary(data):
    """Calculate summary statistics from energy grid data"""
    try:
        grid = data.get("grid", {}).get("features", [])
        
        if not grid:
            return {"total_facilities": 0, "total_capacity_mw": 0, "avg_resilience": 0, "critical_facilities": 0}
        
        # Calculate statistics
        capacities = []
        resilience_scores = []
        critical_count = 0
        
        for facility in grid:
            props = facility.get("properties", {})
            capacity = props.get("capacity_mw", 0)
            resilience = props.get("resilience_score", 0)
            
            capacities.append(capacity)
            resilience_scores.append(resilience)
            
            if resilience < 30:
                critical_count += 1
        
        return {
            "total_facilities": len(grid),
            "total_capacity_mw": round(sum(capacities), 0),
            "avg_resilience": round(sum(resilience_scores) / len(resilience_scores), 1) if resilience_scores else 0,
            "critical_facilities": critical_count
        }
    
    except Exception:
        return {"total_facilities": 0, "total_capacity_mw": 0, "avg_resilience": 0, "critical_facilities": 0}

if __name__ == "__main__":
    print("⚡ Starting Energy Grid Now API server...")
    print("📍 View at: http://localhost:8000")
    print("🗺️  Map interface: http://localhost:8000/")
    print("📊 Public data: http://localhost:8000/public/latest")
    print("🔒 Internal data: http://localhost:8000/internal/latest")
    print("⚠️  Current outages: http://localhost:8000/outages")
    print("🌐 Regional health: http://localhost:8000/regional")
    print("❤️  Health check: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
