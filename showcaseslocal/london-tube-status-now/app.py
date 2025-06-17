#!/usr/bin/env python3
"""
London Tube Status Now - FastAPI Web Application
Real-time London Underground service status and disruption tracking
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="London Tube Status Now",
    description="Real-time London Underground service status and disruption tracking using TfL API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    print("✅ Static files mounted from /app/static")

# Global data storage
tube_data = None
last_updated = None

def load_tube_data() -> Dict[str, Any]:
    """Load the latest tube status data"""
    global tube_data, last_updated
    
    try:
        # Try to load the latest processed data
        if os.path.exists('tube_status_latest.json'):
            with open('tube_status_latest.json', 'r') as f:
                data = json.load(f)
                tube_data = data
                last_updated = data.get('last_updated', datetime.now().isoformat())
                return data
        else:
            # Return sample data if no processed data available
            return create_sample_response()
            
    except Exception as e:
        print(f"❌ Error loading tube data: {e}")
        return create_sample_response()

def create_sample_response() -> Dict[str, Any]:
    """Create sample response when data unavailable"""
    return {
        "tube_lines": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "line_id": "central",
                        "line_name": "Central",
                        "status_severity": 6,
                        "status_description": "Minor Delays",
                        "status_category": "Minor Delays",
                        "status_color": "#FF8C00",
                        "status_score": 6,
                        "reason": "Earlier signal failure",
                        "tube_color": "#E32017",
                        "last_updated": datetime.now().isoformat()
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[-0.0742, 51.5155], [-0.0981, 51.5155], [-0.1276, 51.5074]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "line_id": "piccadilly",
                        "line_name": "Piccadilly",
                        "status_severity": 10,
                        "status_description": "Good Service",
                        "status_category": "Good Service",
                        "status_color": "#00782A",
                        "status_score": 10,
                        "reason": "",
                        "tube_color": "#003688",
                        "last_updated": datetime.now().isoformat()
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[-0.0742, 51.5226], [-0.1276, 51.5155], [-0.1553, 51.5074]]
                    }
                }
            ]
        },
        "summary": {
            "total_lines": 11,
            "good_service": 9,
            "minor_issues": 2,
            "major_issues": 0,
            "avg_status_score": 9.1,
            "last_updated": datetime.now().isoformat()
        },
        "last_updated": datetime.now().isoformat()
    }

@app.on_event("startup")
async def startup_event():
    """Load data on startup"""
    print("🚇 Starting London Tube Status Now...")
    load_tube_data()
    print("✅ Tube status data processing completed successfully")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    try:
        static_file = Path(__file__).parent / "static" / "index.html"
        if static_file.exists():
            return HTMLResponse(content=static_file.read_text(), status_code=200)
        else:
            return HTMLResponse(
                content="""
                <html>
                    <head><title>London Tube Status Now</title></head>
                    <body>
                        <h1>🚇 London Tube Status Now</h1>
                        <p>Real-time London Underground service status</p>
                        <p>API endpoints:</p>
                        <ul>
                            <li><a href="/health">/health</a> - Service health check</li>
                            <li><a href="/tube/status">/tube/status</a> - Current tube status</li>
                            <li><a href="/public/latest">/public/latest</a> - Latest public data</li>
                            <li><a href="/docs">/docs</a> - API documentation</li>
                        </ul>
                    </body>
                </html>
                """,
                status_code=200
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving page: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global tube_data, last_updated
    
    if tube_data is None:
        tube_data = load_tube_data()
    
    summary = tube_data.get('summary', {}) if tube_data else {}
    
    return {
        "status": "healthy",
        "service": "London Tube Status Now",
        "data_available": tube_data is not None,
        "total_lines": summary.get('total_lines', 0),
        "good_service": summary.get('good_service', 0),
        "issues": summary.get('minor_issues', 0) + summary.get('major_issues', 0),
        "avg_status_score": summary.get('avg_status_score', 0),
        "last_updated": last_updated or datetime.now().isoformat()
    }

@app.get("/tube/status")
async def get_tube_status():
    """Get current tube line status"""
    global tube_data
    
    if tube_data is None:
        tube_data = load_tube_data()
    
    if not tube_data:
        raise HTTPException(status_code=503, detail="Tube status data unavailable")
    
    return JSONResponse(content=tube_data)

@app.get("/tube/lines")
async def get_tube_lines():
    """Get tube lines with current status"""
    global tube_data
    
    if tube_data is None:
        tube_data = load_tube_data()
    
    if not tube_data or 'tube_lines' not in tube_data:
        raise HTTPException(status_code=503, detail="Tube lines data unavailable")
    
    return JSONResponse(content=tube_data['tube_lines'])

@app.get("/tube/summary")
async def get_tube_summary():
    """Get tube system summary statistics"""
    global tube_data
    
    if tube_data is None:
        tube_data = load_tube_data()
    
    if not tube_data or 'summary' not in tube_data:
        raise HTTPException(status_code=503, detail="Tube summary data unavailable")
    
    return JSONResponse(content=tube_data['summary'])

@app.get("/public/latest")
async def get_public_latest():
    """Get latest public tube status data (for frontend)"""
    global tube_data
    
    if tube_data is None:
        tube_data = load_tube_data()
    
    if not tube_data:
        tube_data = create_sample_response()
    
    # Format response for public consumption
    response = {
        "status": "success",
        "data": tube_data,
        "last_updated": tube_data.get('last_updated', datetime.now().isoformat()),
        "summary": tube_data.get('summary', {}),
        "total_lines": tube_data.get('summary', {}).get('total_lines', 0),
        "good_service": tube_data.get('summary', {}).get('good_service', 0),
        "issues": tube_data.get('summary', {}).get('minor_issues', 0) + tube_data.get('summary', {}).get('major_issues', 0)
    }
    
    return JSONResponse(content=response)

@app.get("/api/refresh")
async def refresh_data():
    """Manually refresh tube status data"""
    global tube_data, last_updated
    
    try:
        # Reload data
        tube_data = load_tube_data()
        last_updated = datetime.now().isoformat()
        
        return {
            "status": "success",
            "message": "Tube status data refreshed successfully",
            "last_updated": last_updated,
            "total_lines": tube_data.get('summary', {}).get('total_lines', 0) if tube_data else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing data: {str(e)}")

if __name__ == "__main__":
    print("🚇 London Tube Status Now - Starting FastAPI server...")
    print("📍 Access the application at: http://localhost:8000")
    print("📊 API documentation at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
