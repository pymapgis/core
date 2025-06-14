"""
FastAPI Web Service for Supply Chain Optimization

This module provides a REST API for the supply chain optimization functionality,
making it accessible via HTTP requests for integration with other systems.

Author: Nicholas Karlson
License: MIT
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
import json
import os
import tempfile
from datetime import datetime

from .supply_chain_optimizer import SimpleSupplyChainOptimizer, Location


# Pydantic models for API requests/responses
class LocationModel(BaseModel):
    """API model for location data."""
    name: str
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    demand: float = Field(default=0.0, ge=0, description="Demand in units")
    capacity: float = Field(default=0.0, ge=0, description="Capacity in units")
    cost_per_unit: float = Field(default=0.0, ge=0, description="Cost per unit")


class OptimizationRequest(BaseModel):
    """API model for optimization requests."""
    num_customers: int = Field(default=30, ge=1, le=1000, description="Number of customers to generate")
    num_potential_warehouses: int = Field(default=8, ge=1, le=50, description="Number of potential warehouses")
    num_warehouses: int = Field(default=3, ge=1, le=20, description="Number of warehouses to select")
    region_bounds: Tuple[float, float, float, float] = Field(
        default=(40.0, 45.0, -85.0, -75.0),
        description="Region bounds as (min_lat, max_lat, min_lon, max_lon)"
    )
    random_seed: int = Field(default=42, description="Random seed for reproducibility")


class OptimizationResponse(BaseModel):
    """API model for optimization responses."""
    success: bool
    message: str
    optimization_id: str
    summary: Dict
    warehouse_locations: List[LocationModel]
    customer_assignments: Dict[str, str]
    total_cost: float
    total_distance: float
    utilization_rate: float
    generated_at: str


class HealthResponse(BaseModel):
    """API model for health check responses."""
    status: str
    timestamp: str
    version: str


# Initialize FastAPI app
app = FastAPI(
    title="Supply Chain Optimization API",
    description="A simple REST API for supply chain optimization using PyMapGIS",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global storage for optimization results (in production, use a database)
optimization_results: Dict[str, Dict] = {}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic information."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Supply Chain Optimization API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { color: #2c3e50; }
            .endpoint { background-color: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .method { font-weight: bold; color: #27ae60; }
        </style>
    </head>
    <body>
        <h1 class="header">🚚 Supply Chain Optimization API</h1>
        <p>Welcome to the Supply Chain Optimization API powered by PyMapGIS!</p>
        
        <h2>Available Endpoints:</h2>
        <div class="endpoint">
            <span class="method">GET</span> <code>/health</code> - Health check
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <code>/optimize</code> - Run supply chain optimization
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <code>/results/{optimization_id}</code> - Get optimization results
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <code>/map/{optimization_id}</code> - Get interactive map
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <code>/docs</code> - Interactive API documentation
        </div>
        
        <h2>Quick Start:</h2>
        <ol>
            <li>Check API health: <code>GET /health</code></li>
            <li>Run optimization: <code>POST /optimize</code></li>
            <li>View results: <code>GET /results/{optimization_id}</code></li>
            <li>See interactive map: <code>GET /map/{optimization_id}</code></li>
        </ol>
        
        <p><a href="/docs">📚 View Interactive API Documentation</a></p>
    </body>
    </html>
    """
    return html_content


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="0.1.0"
    )


@app.post("/optimize", response_model=OptimizationResponse)
async def optimize_supply_chain(request: OptimizationRequest, background_tasks: BackgroundTasks):
    """
    Run supply chain optimization with the given parameters.
    
    This endpoint generates sample data and optimizes warehouse locations
    to minimize total cost while serving all customer demand.
    """
    try:
        # Generate unique optimization ID
        optimization_id = f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.random_seed}"
        
        # Initialize optimizer
        optimizer = SimpleSupplyChainOptimizer(random_seed=request.random_seed)
        
        # Generate sample data
        optimizer.generate_sample_data(
            num_customers=request.num_customers,
            num_potential_warehouses=request.num_potential_warehouses,
            region_bounds=request.region_bounds
        )
        
        # Run optimization
        solution = optimizer.optimize_warehouse_locations(num_warehouses=request.num_warehouses)
        
        # Generate report
        report = optimizer.generate_report()
        
        # Convert warehouse locations to API models
        warehouse_models = [
            LocationModel(
                name=w.name,
                latitude=w.latitude,
                longitude=w.longitude,
                demand=0.0,  # Warehouses don't have demand
                capacity=w.capacity,
                cost_per_unit=w.cost_per_unit
            )
            for w in solution.warehouse_locations
        ]
        
        # Store results for later retrieval
        optimization_results[optimization_id] = {
            "optimizer": optimizer,
            "solution": solution,
            "report": report,
            "request": request.dict()
        }
        
        # Schedule background task to create map
        background_tasks.add_task(create_map_file, optimization_id, optimizer)
        
        return OptimizationResponse(
            success=True,
            message="Optimization completed successfully",
            optimization_id=optimization_id,
            summary=report["optimization_summary"],
            warehouse_locations=warehouse_models,
            customer_assignments=solution.customer_assignments,
            total_cost=solution.total_cost,
            total_distance=solution.total_distance,
            utilization_rate=solution.utilization_rate,
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.get("/results/{optimization_id}")
async def get_optimization_results(optimization_id: str):
    """Get detailed results for a specific optimization run."""
    if optimization_id not in optimization_results:
        raise HTTPException(status_code=404, detail="Optimization ID not found")
    
    result = optimization_results[optimization_id]
    return {
        "optimization_id": optimization_id,
        "report": result["report"],
        "request_parameters": result["request"]
    }


@app.get("/map/{optimization_id}")
async def get_optimization_map(optimization_id: str):
    """Get the interactive map for a specific optimization run."""
    if optimization_id not in optimization_results:
        raise HTTPException(status_code=404, detail="Optimization ID not found")
    
    map_file = f"/tmp/map_{optimization_id}.html"
    
    if not os.path.exists(map_file):
        # Generate map if it doesn't exist
        optimizer = optimization_results[optimization_id]["optimizer"]
        optimizer.create_visualization(save_path=map_file)
    
    return FileResponse(
        map_file,
        media_type="text/html",
        filename=f"supply_chain_map_{optimization_id}.html"
    )


@app.get("/list")
async def list_optimizations():
    """List all available optimization results."""
    return {
        "optimizations": [
            {
                "optimization_id": opt_id,
                "generated_at": result["report"]["generated_at"],
                "total_cost": result["solution"].total_cost,
                "num_warehouses": len(result["solution"].warehouse_locations),
                "num_customers": len(result["optimizer"].customers)
            }
            for opt_id, result in optimization_results.items()
        ]
    }


async def create_map_file(optimization_id: str, optimizer: SimpleSupplyChainOptimizer):
    """Background task to create map file."""
    try:
        map_file = f"/tmp/map_{optimization_id}.html"
        optimizer.create_visualization(save_path=map_file)
    except Exception as e:
        print(f"Error creating map for {optimization_id}: {e}")


# Add CORS middleware for web browser access
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
