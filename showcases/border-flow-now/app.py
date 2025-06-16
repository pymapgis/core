#!/usr/bin/env python3
"""
Border Flow Now - FastAPI Web Application
Real-time CBP border wait times visualization
"""

import json
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()

# Initialize FastAPI app
app = FastAPI(
    title="Border Flow Now",
    description="Real-time CBP border wait times and congestion analysis",
    version="1.0.0"
)

# Mount static files with absolute path
static_dir = SCRIPT_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

def load_border_data():
    """Load the latest border impact data"""
    try:
        data_file = SCRIPT_DIR / "border_latest.json"
        if data_file.exists():
            with open(data_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "status": "error",
                "message": "No data available. Run border_worker.py first.",
                "data": None,
                "last_updated": None,
                "total_ports": 0
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error loading data: {str(e)}",
            "data": None,
            "last_updated": None,
            "total_ports": 0
        }

@app.get("/")
async def root():
    """Serve the main map interface"""
    index_file = SCRIPT_DIR / "static" / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        return JSONResponse({
            "message": "Border Flow Now API",
            "status": "running",
            "endpoints": {
                "map": "/",
                "public_data": "/public/latest",
                "internal_data": "/internal/latest",
                "health": "/health"
            }
        })

@app.get("/public/latest")
async def get_public_data():
    """Get latest border wait times data (public access)"""
    data = load_border_data()
    
    if data["status"] == "success" and data["data"]:
        # Return simplified public data
        public_data = {
            "status": "success",
            "data": data["data"],
            "last_updated": data["last_updated"],
            "total_ports": data["total_ports"],
            "summary": {
                "avg_wait_time": data.get("avg_wait_time", 0),
                "max_wait_time": data.get("max_wait_time", 0)
            }
        }
        return JSONResponse(public_data)
    else:
        return JSONResponse({
            "status": "error",
            "message": "Border wait time data not available",
            "data": None
        }, status_code=404)

@app.get("/internal/latest")
async def get_internal_data():
    """Get full border data with metadata (internal access)"""
    data = load_border_data()
    return JSONResponse(data)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    data = load_border_data()
    data_available = data["status"] == "success" and data["data"] is not None
    
    return JSONResponse({
        "status": "healthy",
        "service": "Border Flow Now",
        "data_available": data_available,
        "total_ports": data.get("total_ports", 0),
        "last_updated": data.get("last_updated")
    })

@app.get("/api/docs")
async def api_documentation():
    """API documentation"""
    return JSONResponse({
        "title": "Border Flow Now API",
        "version": "1.0.0",
        "description": "Real-time CBP border wait times and congestion analysis",
        "endpoints": {
            "GET /": "Main map interface",
            "GET /public/latest": "Latest border wait times (public)",
            "GET /internal/latest": "Full data with metadata (internal)",
            "GET /health": "Service health check",
            "GET /api/docs": "This documentation"
        },
        "data_sources": {
            "cbp_api": "https://bwt.cbp.gov/api/bwt",
            "description": "U.S. Customs and Border Protection Border Wait Times"
        },
        "features": [
            "Real-time border wait time monitoring",
            "Congestion score calculation",
            "Interactive map visualization",
            "RESTful API access",
            "Health monitoring"
        ]
    })

if __name__ == "__main__":
    print("🚛 Starting Border Flow Now API server...")
    print("📍 View at: http://localhost:8000")
    print("🗺️  Map interface: http://localhost:8000/")
    print("📊 Public data: http://localhost:8000/public/latest")
    print("🔒 Internal data: http://localhost:8000/internal/latest")
    print("❤️  Health check: http://localhost:8000/health")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
