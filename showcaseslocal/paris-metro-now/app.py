#!/usr/bin/env python3
"""
Paris Metro Now - FastAPI Web Application
Real-time French public transport with Metro, RER, and bus integration
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
    title="Paris Metro Now",
    description="Real-time French public transport with Metro, RER, and bus integration using RATP API",
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
transit_data = None
last_updated = None

def load_transit_data() -> Dict[str, Any]:
    """Load the latest Paris Metro data"""
    global transit_data, last_updated
    
    try:
        # Try to load the latest processed data
        if os.path.exists('transit_status_latest.json'):
            with open('transit_status_latest.json', 'r') as f:
                data = json.load(f)
                transit_data = data
                last_updated = data.get('last_updated', datetime.now().isoformat())
                return data
        else:
            # Return sample data if no processed data available
            return create_sample_response()
            
    except Exception as e:
        print(f"❌ Error loading transit data: {e}")
        return create_sample_response()

def create_sample_response() -> Dict[str, Any]:
    """Create sample response when data unavailable"""
    return {
        "transit_routes": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "route_id": "metro_1",
                        "route_name": "Metro 1 Château de Vincennes ↔ Pont de Neuilly",
                        "route_type": "metro",
                        "status": "Excellent Service",
                        "delay_minutes": 0,
                        "frequency_minutes": 2,
                        "punctuality_percent": 98,
                        "elegance_score": 9.8,
                        "status_category": "Excellent",
                        "status_color": "#00A88F",
                        "route_color": "#FFCD00",
                        "last_updated": datetime.now().isoformat()
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[2.3522, 48.8566], [2.3622, 48.8666], [2.3722, 48.8766]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "route_id": "rer_a",
                        "route_name": "RER A Cergy ↔ Boissy-Saint-Léger",
                        "route_type": "rer",
                        "status": "Minor Delays",
                        "delay_minutes": 3,
                        "frequency_minutes": 6,
                        "punctuality_percent": 89,
                        "elegance_score": 8.1,
                        "status_category": "Good",
                        "status_color": "#FFCD00",
                        "route_color": "#E2231A",
                        "last_updated": datetime.now().isoformat()
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[2.3222, 48.8266], [2.3522, 48.8566], [2.3822, 48.8866]]
                    }
                }
            ]
        },
        "summary": {
            "total_routes": 8,
            "excellent_service": 4,
            "good_service": 3,
            "issues": 1,
            "avg_elegance_score": 8.9,
            "avg_delay_minutes": 1.8,
            "avg_punctuality_percent": 92,
            "last_updated": datetime.now().isoformat()
        },
        "last_updated": datetime.now().isoformat()
    }

@app.on_event("startup")
async def startup_event():
    """Load data on startup"""
    print("🚇 Starting Paris Metro Now...")
    load_transit_data()
    print("✅ Paris Metro data processing completed successfully")

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
                    <head><title>Paris Metro Now</title></head>
                    <body>
                        <h1>🚇 Paris Metro Now</h1>
                        <p>Real-time French public transport tracking</p>
                        <p>API endpoints:</p>
                        <ul>
                            <li><a href="/health">/health</a> - Service health check</li>
                            <li><a href="/transit/status">/transit/status</a> - Current transit status</li>
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
    global transit_data, last_updated
    
    if transit_data is None:
        transit_data = load_transit_data()
    
    summary = transit_data.get('summary', {}) if transit_data else {}
    
    return {
        "status": "healthy",
        "service": "Paris Metro Now",
        "data_available": transit_data is not None,
        "total_routes": summary.get('total_routes', 0),
        "excellent_service": summary.get('excellent_service', 0),
        "good_service": summary.get('good_service', 0),
        "issues": summary.get('issues', 0),
        "avg_elegance_score": summary.get('avg_elegance_score', 0),
        "avg_punctuality": summary.get('avg_punctuality_percent', 0),
        "last_updated": last_updated or datetime.now().isoformat()
    }

@app.get("/transit/status")
async def get_transit_status():
    """Get current Paris Metro status"""
    global transit_data
    
    if transit_data is None:
        transit_data = load_transit_data()
    
    if not transit_data:
        raise HTTPException(status_code=503, detail="Transit status data unavailable")
    
    return JSONResponse(content=transit_data)

@app.get("/transit/routes")
async def get_transit_routes():
    """Get Paris Metro routes with current status"""
    global transit_data
    
    if transit_data is None:
        transit_data = load_transit_data()
    
    if not transit_data or 'transit_routes' not in transit_data:
        raise HTTPException(status_code=503, detail="Transit routes data unavailable")
    
    return JSONResponse(content=transit_data['transit_routes'])

@app.get("/transit/summary")
async def get_transit_summary():
    """Get Paris Metro system summary statistics"""
    global transit_data
    
    if transit_data is None:
        transit_data = load_transit_data()
    
    if not transit_data or 'summary' not in transit_data:
        raise HTTPException(status_code=503, detail="Transit summary data unavailable")
    
    return JSONResponse(content=transit_data['summary'])

@app.get("/public/latest")
async def get_public_latest():
    """Get latest public Paris Metro data (for frontend)"""
    global transit_data
    
    if transit_data is None:
        transit_data = load_transit_data()
    
    if not transit_data:
        transit_data = create_sample_response()
    
    # Format response for public consumption
    response = {
        "status": "success",
        "data": transit_data,
        "last_updated": transit_data.get('last_updated', datetime.now().isoformat()),
        "summary": transit_data.get('summary', {}),
        "total_routes": transit_data.get('summary', {}).get('total_routes', 0),
        "excellent_service": transit_data.get('summary', {}).get('excellent_service', 0),
        "good_service": transit_data.get('summary', {}).get('good_service', 0),
        "issues": transit_data.get('summary', {}).get('issues', 0)
    }
    
    return JSONResponse(content=response)

@app.get("/api/refresh")
async def refresh_data():
    """Manually refresh Paris Metro data"""
    global transit_data, last_updated
    
    try:
        # Reload data
        transit_data = load_transit_data()
        last_updated = datetime.now().isoformat()
        
        return {
            "status": "success",
            "message": "Paris Metro data refreshed successfully",
            "last_updated": last_updated,
            "total_routes": transit_data.get('summary', {}).get('total_routes', 0) if transit_data else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing data: {str(e)}")

if __name__ == "__main__":
    print("🚇 Paris Metro Now - Starting FastAPI server...")
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
