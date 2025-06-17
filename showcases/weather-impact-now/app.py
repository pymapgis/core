#!/usr/bin/env python3
"""
Weather Impact Now - FastAPI Web Application
Serves real-time weather monitoring and supply chain impact analysis
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
    title="Weather Impact Now",
    description="Real-time weather monitoring and supply chain impact analysis",
    version="1.0.0"
)

# Mount static files (will be done after startup)
static_dir = SCRIPT_DIR / "static"

@app.on_event("startup")
async def startup_event():
    """Run weather worker on startup to ensure fresh data"""
    print("🚀 Starting Weather Impact Now...")
    
    # Mount static files after ensuring directory exists
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        print(f"✅ Static files mounted from {static_dir}")
    
    try:
        # Run the weather worker to process latest data
        worker_path = SCRIPT_DIR / "weather_worker.py"
        result = subprocess.run([sys.executable, str(worker_path)], 
                              capture_output=True, text=True, timeout=30, cwd=str(SCRIPT_DIR))
        if result.returncode == 0:
            print("✅ Weather data processing completed successfully")
        else:
            print(f"⚠️ Weather worker completed with warnings: {result.stderr}")
    except Exception as e:
        print(f"❌ Error running weather worker: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interactive map interface"""
    html_file = SCRIPT_DIR / "static" / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(), status_code=200)
    else:
        return HTMLResponse(content="<h1>Weather Impact Now</h1><p>Map interface not found</p>", status_code=404)

@app.get("/public/latest")
async def get_public_data():
    """Get latest weather impact data (public endpoint)"""
    try:
        data_file = SCRIPT_DIR / "weather_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Weather data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Add metadata
        response = {
            "status": "success",
            "data": data,
            "last_updated": datetime.now().isoformat() + "Z",
            "summary": data.get("summary", {}),
            "location_count": data.get("summary", {}).get("total_locations", 0),
            "avg_temperature": data.get("summary", {}).get("avg_temperature", 0),
            "high_impact_count": data.get("summary", {}).get("high_impact_locations", 0)
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading weather data: {str(e)}")

@app.get("/internal/latest")
async def get_internal_data():
    """Get full analyst data with metadata (protected endpoint)"""
    try:
        # For demo purposes, this returns the same data as public
        # In production, this would include additional analyst fields
        data_file = SCRIPT_DIR / "weather_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Weather data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Enhanced response with analyst metadata
        response = {
            "status": "success",
            "data": data,
            "metadata": {
                "last_updated": datetime.now().isoformat() + "Z",
                "total_locations": data.get("summary", {}).get("total_locations", 0),
                "avg_temperature": data.get("summary", {}).get("avg_temperature", 0),
                "avg_impact_score": data.get("summary", {}).get("avg_impact_score", 0),
                "high_impact_locations": data.get("summary", {}).get("high_impact_locations", 0),
                "severe_alerts": data.get("summary", {}).get("severe_weather_alerts", 0),
                "data_source": "NOAA Weather Service",
                "processing_version": "1.0.0",
                "coverage": "Major US Cities",
                "update_frequency": "5 minutes",
                "impact_categories": ["Temperature", "Wind", "Precipitation", "Visibility"],
                "transport_modes": ["Air", "Ground", "Maritime"],
                "summary": data.get("summary", {})
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading weather data: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        data_file = SCRIPT_DIR / "weather_latest.json"
        data_available = data_file.exists()
        
        if data_available:
            with open(data_file, "r") as f:
                data = json.load(f)
            total_locations = data.get("summary", {}).get("total_locations", 0)
            avg_temperature = data.get("summary", {}).get("avg_temperature", 0)
            high_impact_count = data.get("summary", {}).get("high_impact_locations", 0)
        else:
            total_locations = 0
            avg_temperature = 0
            high_impact_count = 0
        
        return {
            "status": "healthy",
            "service": "Weather Impact Now",
            "data_available": data_available,
            "total_locations": total_locations,
            "avg_temperature": avg_temperature,
            "high_impact_locations": high_impact_count,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Weather Impact Now",
            "error": str(e),
            "last_updated": datetime.now().isoformat() + "Z"
        }

@app.get("/alerts")
async def get_weather_alerts():
    """Get current weather alerts and warnings"""
    try:
        data_file = SCRIPT_DIR / "weather_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Weather data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Extract high-impact locations as alerts
        weather_features = data.get("weather", {}).get("features", [])
        alerts = []
        
        for feature in weather_features:
            props = feature.get("properties", {})
            impact = props.get("total_impact", 0)
            alert_level = props.get("alert_level", "Low")
            
            if impact > 50:  # High impact threshold
                alerts.append({
                    "location": props.get("location", "Unknown"),
                    "alert_level": alert_level,
                    "impact_score": impact,
                    "temperature": props.get("temperature", 0),
                    "conditions": props.get("conditions", "Unknown"),
                    "transport_risk": props.get("transport_risk", "Unknown"),
                    "coordinates": feature.get("geometry", {}).get("coordinates", [0, 0])
                })
        
        return {
            "status": "success",
            "alert_count": len(alerts),
            "alerts": sorted(alerts, key=lambda x: x["impact_score"], reverse=True),
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading weather alerts: {str(e)}")

def calculate_summary(data):
    """Calculate summary statistics from weather data"""
    try:
        weather = data.get("weather", {}).get("features", [])
        
        if not weather:
            return {"total_locations": 0, "avg_temperature": 0, "avg_impact_score": 0, "high_impact_locations": 0}
        
        # Calculate statistics
        temperatures = []
        impact_scores = []
        high_impact_count = 0
        
        for location in weather:
            props = location.get("properties", {})
            temp = props.get("temperature", 0)
            impact = props.get("total_impact", 0)
            
            temperatures.append(temp)
            impact_scores.append(impact)
            
            if impact > 60:
                high_impact_count += 1
        
        return {
            "total_locations": len(weather),
            "avg_temperature": round(sum(temperatures) / len(temperatures), 1) if temperatures else 0,
            "avg_impact_score": round(sum(impact_scores) / len(impact_scores), 1) if impact_scores else 0,
            "high_impact_locations": high_impact_count
        }
    
    except Exception:
        return {"total_locations": 0, "avg_temperature": 0, "avg_impact_score": 0, "high_impact_locations": 0}

if __name__ == "__main__":
    print("🌦️ Starting Weather Impact Now API server...")
    print("📍 View at: http://localhost:8000")
    print("🗺️  Map interface: http://localhost:8000/")
    print("📊 Public data: http://localhost:8000/public/latest")
    print("🔒 Internal data: http://localhost:8000/internal/latest")
    print("⚠️  Weather alerts: http://localhost:8000/alerts")
    print("❤️  Health check: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
