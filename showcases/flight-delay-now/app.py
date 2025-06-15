#!/usr/bin/env python3
"""
FastAPI Web Application for Flight Delay Now

Serves:
- GET /public/tiles/{z}/{x}/{y}.pbf - Anonymous map layer (vector tiles)
- GET /internal/latest - JWT-protected full GeoJSON for analysts
- GET / - Interactive web viewer with MapLibre GL JS
- GET /health - Health check endpoint

~15 lines of FastAPI routes as specified in requirements.
"""

from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import Response, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from pathlib import Path
from datetime import datetime
import logging

# Import our flight worker
from flight_worker import main as process_flight_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Flight Delay Now",
    description="Live flight delay monitoring at major US airports using PyMapGIS",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data storage
latest_data = None
last_updated = None
processing_lock = asyncio.Lock()


async def load_latest_data():
    """Load the latest flight delay data."""
    global latest_data, last_updated
    
    try:
        if Path("delay_latest.geojson").exists():
            with open("delay_latest.geojson", "r") as f:
                latest_data = json.load(f)
            last_updated = Path("delay_latest.geojson").stat().st_mtime
            logger.info("Loaded latest flight delay data")
        else:
            logger.warning("No delay_latest.geojson file found")
            latest_data = {"type": "FeatureCollection", "features": []}
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        latest_data = {"type": "FeatureCollection", "features": []}


async def refresh_data_background():
    """Background task to refresh flight delay data."""
    async with processing_lock:
        try:
            logger.info("Starting background data refresh...")
            await process_flight_data()
            await load_latest_data()
            logger.info("Background data refresh completed")
        except Exception as e:
            logger.error(f"Error in background refresh: {e}")


# Load data on startup
@app.on_event("startup")
async def startup_event():
    await load_latest_data()
    # Start background refresh every 2 minutes
    asyncio.create_task(periodic_refresh())


async def periodic_refresh():
    """Periodically refresh data every 2 minutes."""
    while True:
        await asyncio.sleep(120)  # 2 minutes
        await refresh_data_background()


# Simple JWT verification (demo purposes)
def jwt_verify(request: Request):
    """Simple JWT verification for demo purposes."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    if token != "demo-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"user": "demo_user", "token": token}


@app.get("/public/tiles/{z}/{x}/{y}.pbf")
async def get_public_tiles(z: int, x: int, y: int):
    """Serve public vector tiles for anonymous access."""
    # For demo, return GeoJSON as simplified tiles
    # In production, implement proper MVT generation
    if latest_data:
        return Response(
            content=json.dumps(latest_data).encode(),
            media_type="application/json"
        )
    return Response(content=b'{"type":"FeatureCollection","features":[]}', media_type="application/json")


@app.get("/internal/latest")
async def get_latest_data(user=Depends(jwt_verify)):
    """Get latest flight delay data (JWT protected)."""
    if latest_data is None:
        await load_latest_data()
    
    return {
        "data": latest_data,
        "last_updated": last_updated,
        "user": user["user"],
        "airports_count": len(latest_data.get("features", []))
    }


@app.get("/refresh")
async def manual_refresh(background_tasks: BackgroundTasks):
    """Manually trigger data refresh."""
    background_tasks.add_task(refresh_data_background)
    return {"message": "Data refresh initiated"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    data_status = "ok" if Path("delay_latest.geojson").exists() else "no_data"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "flight-delay-now",
        "checks": {
            "data_file": data_status,
            "airports_count": len(latest_data.get("features", [])) if latest_data else 0,
            "last_updated": datetime.fromtimestamp(last_updated).isoformat() if last_updated else None
        }
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interactive viewer with MapLibre GL JS."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>Flight Delay Now</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://unpkg.com/maplibre-gl@3.6.0/dist/maplibre-gl.js"></script>
        <link href="https://unpkg.com/maplibre-gl@3.6.0/dist/maplibre-gl.css" rel="stylesheet" />
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
            #map { position: absolute; top: 0; bottom: 0; width: 100%; }
        </style>
    </head>
    <body class="bg-gray-900">
        <div id="map"></div>
        
        <!-- Info Panel -->
        <div class="absolute top-4 left-4 bg-white bg-opacity-90 backdrop-blur-sm rounded-lg p-4 shadow-lg max-w-sm z-10">
            <h3 class="text-lg font-bold text-gray-800 mb-2">✈️ Flight Delay Now</h3>
            <p class="text-sm text-gray-600 mb-2">Live departure delays at major US airports</p>
            <p class="text-xs text-gray-500"><strong>Data:</strong> FAA OIS + Individual Airport APIs</p>
            <p class="text-xs text-gray-500"><strong>Updates:</strong> Every 2 minutes</p>
            <p class="text-xs text-gray-500 mt-2"><em>Click airports for details</em></p>
        </div>
        
        <!-- Legend -->
        <div class="absolute bottom-4 right-4 bg-white bg-opacity-90 backdrop-blur-sm rounded-lg p-4 shadow-lg z-10">
            <h4 class="font-semibold text-gray-800 mb-2">Delay Status</h4>
            <div class="space-y-2 text-sm">
                <div class="flex items-center">
                    <div class="w-4 h-4 bg-green-500 rounded-full mr-2"></div>
                    <span>On-time (&lt;15 min)</span>
                </div>
                <div class="flex items-center">
                    <div class="w-4 h-4 bg-yellow-500 rounded-full mr-2"></div>
                    <span>Moderate (15-30 min)</span>
                </div>
                <div class="flex items-center">
                    <div class="w-4 h-4 bg-red-500 rounded-full mr-2"></div>
                    <span>Severe (&gt;30 min)</span>
                </div>
            </div>
        </div>
        
        <!-- Refresh Button -->
        <div class="absolute top-4 right-4 z-10">
            <button id="refreshBtn" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg shadow-lg transition-colors">
                🔄 Refresh
            </button>
        </div>
        
        <script>
            // Initialize dark map
            const map = new maplibregl.Map({
                container: 'map',
                style: {
                    version: 8,
                    sources: {
                        'dark': {
                            type: 'raster',
                            tiles: ['https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png'],
                            tileSize: 256,
                            attribution: '© CartoDB'
                        }
                    },
                    layers: [{
                        id: 'dark',
                        type: 'raster',
                        source: 'dark'
                    }]
                },
                center: [-98.5795, 39.8283], // Center of US
                zoom: 4
            });

            map.addControl(new maplibregl.NavigationControl());

            // Load flight delay data
            async function loadFlightData() {
                try {
                    const response = await fetch('/public/tiles/0/0/0.pbf');
                    const data = await response.json();
                    
                    if (map.getSource('airports')) {
                        map.getSource('airports').setData(data);
                    } else {
                        map.addSource('airports', {
                            type: 'geojson',
                            data: data
                        });
                        
                        // Add airport circles
                        map.addLayer({
                            id: 'airport-circles',
                            type: 'circle',
                            source: 'airports',
                            paint: {
                                'circle-radius': [
                                    'interpolate',
                                    ['linear'],
                                    ['get', 'DelayScore'],
                                    0, 8,
                                    5, 15,
                                    10, 25
                                ],
                                'circle-color': [
                                    'case',
                                    ['>', ['get', 'avg_dep_delay'], 30], '#ef4444', // red for severe
                                    ['>', ['get', 'avg_dep_delay'], 15], '#eab308', // yellow for moderate  
                                    '#22c55e' // green for on-time
                                ],
                                'circle-opacity': 0.8,
                                'circle-stroke-width': 2,
                                'circle-stroke-color': '#ffffff'
                            }
                        });
                        
                        // Add airport labels
                        map.addLayer({
                            id: 'airport-labels',
                            type: 'symbol',
                            source: 'airports',
                            layout: {
                                'text-field': ['get', 'iata'],
                                'text-font': ['Open Sans Bold'],
                                'text-size': 12,
                                'text-offset': [0, 2]
                            },
                            paint: {
                                'text-color': '#ffffff',
                                'text-halo-color': '#000000',
                                'text-halo-width': 1
                            }
                        });
                    }
                    
                    // Add click handlers
                    map.on('click', 'airport-circles', (e) => {
                        const props = e.features[0].properties;
                        const delayText = props.avg_dep_delay > 0 ? 
                            `Avg dep delay ${Math.round(props.avg_dep_delay)} min` : 
                            'On-time departures';
                        
                        new maplibregl.Popup()
                            .setLngLat(e.lngLat)
                            .setHTML(`
                                <div class="p-2">
                                    <h3 class="font-bold">${props.iata} • ${delayText}</h3>
                                    <p class="text-sm">${props.name}</p>
                                    <p class="text-sm">${props.city}, ${props.state}</p>
                                    <p class="text-sm mt-1"><strong>Flights:</strong> ${props.flights_total || 0}</p>
                                    <p class="text-sm"><strong>Delay Score:</strong> ${props.DelayScore || 0}</p>
                                </div>
                            `)
                            .addTo(map);
                    });
                    
                    map.on('mouseenter', 'airport-circles', () => {
                        map.getCanvas().style.cursor = 'pointer';
                    });
                    
                    map.on('mouseleave', 'airport-circles', () => {
                        map.getCanvas().style.cursor = '';
                    });
                    
                } catch (error) {
                    console.error('Error loading flight data:', error);
                }
            }
            
            // Load data when map is ready
            map.on('load', loadFlightData);
            
            // Refresh button handler
            document.getElementById('refreshBtn').addEventListener('click', async () => {
                const btn = document.getElementById('refreshBtn');
                btn.textContent = '⏳ Refreshing...';
                btn.disabled = true;
                
                try {
                    await fetch('/refresh');
                    setTimeout(() => {
                        loadFlightData();
                        btn.textContent = '🔄 Refresh';
                        btn.disabled = false;
                    }, 2000);
                } catch (error) {
                    console.error('Refresh error:', error);
                    btn.textContent = '🔄 Refresh';
                    btn.disabled = false;
                }
            });
            
            // Auto-refresh every 2 minutes
            setInterval(loadFlightData, 120000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
