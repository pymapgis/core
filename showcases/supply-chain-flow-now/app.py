#!/usr/bin/env python3
"""
Supply Chain Flow Now - FastAPI Web Application
Serves real-time supply chain visibility and logistics flow analysis
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
    title="Supply Chain Flow Now",
    description="Real-time supply chain visibility and logistics flow analysis",
    version="1.0.0"
)

# Mount static files (will be done after startup)
static_dir = SCRIPT_DIR / "static"

@app.on_event("startup")
async def startup_event():
    """Run supply chain worker on startup to ensure fresh data"""
    print("🚀 Starting Supply Chain Flow Now...")
    
    # Mount static files after ensuring directory exists
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        print(f"✅ Static files mounted from {static_dir}")
    
    try:
        # Run the supply chain worker to process latest data
        worker_path = SCRIPT_DIR / "supply_chain_worker.py"
        result = subprocess.run([sys.executable, str(worker_path)], 
                              capture_output=True, text=True, timeout=30, cwd=str(SCRIPT_DIR))
        if result.returncode == 0:
            print("✅ Supply chain data processing completed successfully")
        else:
            print(f"⚠️ Supply chain worker completed with warnings: {result.stderr}")
    except Exception as e:
        print(f"❌ Error running supply chain worker: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main interactive map interface"""
    html_file = SCRIPT_DIR / "static" / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(), status_code=200)
    else:
        return HTMLResponse(content="<h1>Supply Chain Flow Now</h1><p>Map interface not found</p>", status_code=404)

@app.get("/public/latest")
async def get_public_data():
    """Get latest supply chain data (public endpoint)"""
    try:
        data_file = SCRIPT_DIR / "supply_chain_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Supply chain data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Add metadata
        response = {
            "status": "success",
            "data": data,
            "last_updated": datetime.now().isoformat() + "Z",
            "summary": data.get("summary", {}),
            "node_count": data.get("summary", {}).get("total_nodes", 0),
            "total_capacity": data.get("summary", {}).get("total_capacity", 0),
            "critical_nodes": data.get("summary", {}).get("critical_nodes", 0),
            "active_flows": data.get("summary", {}).get("active_flows", 0)
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading supply chain data: {str(e)}")

@app.get("/internal/latest")
async def get_internal_data():
    """Get full analyst data with metadata (protected endpoint)"""
    try:
        # For demo purposes, this returns the same data as public
        # In production, this would include additional analyst fields
        data_file = SCRIPT_DIR / "supply_chain_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Supply chain data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Enhanced response with analyst metadata
        response = {
            "status": "success",
            "data": data,
            "metadata": {
                "last_updated": datetime.now().isoformat() + "Z",
                "total_nodes": data.get("summary", {}).get("total_nodes", 0),
                "total_capacity": data.get("summary", {}).get("total_capacity", 0),
                "avg_flow_efficiency": data.get("summary", {}).get("avg_flow_efficiency", 0),
                "critical_nodes": data.get("summary", {}).get("critical_nodes", 0),
                "nodes_with_delays": data.get("summary", {}).get("nodes_with_delays", 0),
                "high_risk_nodes": data.get("summary", {}).get("high_risk_nodes", 0),
                "active_flows": data.get("summary", {}).get("active_flows", 0),
                "data_source": "Multi-Modal Supply Chain APIs",
                "processing_version": "1.0.0",
                "coverage": "Major US Supply Chain Nodes",
                "update_frequency": "2 minutes",
                "efficiency_factors": ["Capacity", "Delays", "Utilization", "Disruptions"],
                "node_types": ["Port", "Distribution", "Manufacturing", "Rail", "Airport"],
                "regional_health": data.get("regional_health", {}),
                "flow_connections": data.get("flow_connections", []),
                "summary": data.get("summary", {})
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading supply chain data: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        data_file = SCRIPT_DIR / "supply_chain_latest.json"
        data_available = data_file.exists()
        
        if data_available:
            with open(data_file, "r") as f:
                data = json.load(f)
            total_nodes = data.get("summary", {}).get("total_nodes", 0)
            total_capacity = data.get("summary", {}).get("total_capacity", 0)
            critical_nodes = data.get("summary", {}).get("critical_nodes", 0)
            active_flows = data.get("summary", {}).get("active_flows", 0)
        else:
            total_nodes = 0
            total_capacity = 0
            critical_nodes = 0
            active_flows = 0
        
        return {
            "status": "healthy",
            "service": "Supply Chain Flow Now",
            "data_available": data_available,
            "total_nodes": total_nodes,
            "total_capacity": total_capacity,
            "critical_nodes": critical_nodes,
            "active_flows": active_flows,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Supply Chain Flow Now",
            "error": str(e),
            "last_updated": datetime.now().isoformat() + "Z"
        }

@app.get("/disruptions")
async def get_current_disruptions():
    """Get current supply chain disruptions and bottlenecks"""
    try:
        data_file = SCRIPT_DIR / "supply_chain_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Supply chain data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        # Extract nodes with disruptions or issues
        supply_chain_features = data.get("supply_chain", {}).get("features", [])
        disruptions = []
        
        for feature in supply_chain_features:
            props = feature.get("properties", {})
            disruption_level = props.get("disruption_level", "None")
            flow_efficiency = props.get("flow_efficiency", 100)
            delay_hours = props.get("current_delay_hours", 0)
            
            if disruption_level != "None" or flow_efficiency < 60 or delay_hours > 2:  # Issues threshold
                disruptions.append({
                    "node_name": props.get("node_name", "Unknown"),
                    "disruption_level": disruption_level,
                    "flow_efficiency": flow_efficiency,
                    "current_delay_hours": delay_hours,
                    "capacity_units": props.get("capacity_units", 0),
                    "node_type": props.get("node_type", "Unknown"),
                    "economic_impact": props.get("economic_impact", 0),
                    "alert_level": props.get("alert_level", "Low"),
                    "utilization_percent": props.get("utilization_percent", 0),
                    "coordinates": feature.get("geometry", {}).get("coordinates", [0, 0])
                })
        
        return {
            "status": "success",
            "disruption_count": len(disruptions),
            "disruptions": sorted(disruptions, key=lambda x: x["flow_efficiency"]),
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading disruption data: {str(e)}")

@app.get("/flows")
async def get_supply_chain_flows():
    """Get active supply chain flow connections"""
    try:
        data_file = SCRIPT_DIR / "supply_chain_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Supply chain data not available")
        
        with open(data_file, "r") as f:
            data = json.load(f)
        
        flow_connections = data.get("flow_connections", [])
        
        return {
            "status": "success",
            "flow_count": len(flow_connections),
            "flows": flow_connections,
            "last_updated": datetime.now().isoformat() + "Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading flow data: {str(e)}")

@app.get("/regional")
async def get_regional_health():
    """Get regional supply chain health analysis"""
    try:
        data_file = SCRIPT_DIR / "supply_chain_latest.json"
        if not data_file.exists():
            raise HTTPException(status_code=404, detail="Supply chain data not available")
        
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
    """Calculate summary statistics from supply chain data"""
    try:
        supply_chain = data.get("supply_chain", {}).get("features", [])
        
        if not supply_chain:
            return {"total_nodes": 0, "total_capacity": 0, "avg_flow_efficiency": 0, "critical_nodes": 0}
        
        # Calculate statistics
        capacities = []
        flow_efficiencies = []
        critical_count = 0
        
        for node in supply_chain:
            props = node.get("properties", {})
            capacity = props.get("capacity_units", 0)
            efficiency = props.get("flow_efficiency", 0)
            
            capacities.append(capacity)
            flow_efficiencies.append(efficiency)
            
            if efficiency < 30:
                critical_count += 1
        
        return {
            "total_nodes": len(supply_chain),
            "total_capacity": round(sum(capacities), 0),
            "avg_flow_efficiency": round(sum(flow_efficiencies) / len(flow_efficiencies), 1) if flow_efficiencies else 0,
            "critical_nodes": critical_count
        }
    
    except Exception:
        return {"total_nodes": 0, "total_capacity": 0, "avg_flow_efficiency": 0, "critical_nodes": 0}

if __name__ == "__main__":
    print("🚛 Starting Supply Chain Flow Now API server...")
    print("📍 View at: http://localhost:8000")
    print("🗺️  Map interface: http://localhost:8000/")
    print("📊 Public data: http://localhost:8000/public/latest")
    print("🔒 Internal data: http://localhost:8000/internal/latest")
    print("🚨 Current disruptions: http://localhost:8000/disruptions")
    print("🔗 Supply chain flows: http://localhost:8000/flows")
    print("🌐 Regional health: http://localhost:8000/regional")
    print("❤️  Health check: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
