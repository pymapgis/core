# 🔌 API Development

## Comprehensive Guide to Supply Chain API Design and Implementation

This guide provides complete coverage of API development for PyMapGIS logistics applications, including RESTful APIs, GraphQL, real-time APIs, and enterprise integration patterns.

### 1. API Architecture and Design Principles

#### RESTful API Design
```python
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import pymapgis as pmg

app = FastAPI(
    title="PyMapGIS Logistics API",
    description="Comprehensive logistics and supply chain API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class VehicleCreate(BaseModel):
    vehicle_id: str = Field(..., description="Unique vehicle identifier")
    type: str = Field(..., description="Vehicle type (truck, van, etc.)")
    capacity_weight: float = Field(..., gt=0, description="Weight capacity in kg")
    capacity_volume: float = Field(..., gt=0, description="Volume capacity in m³")
    fuel_type: str = Field(..., description="Fuel type (diesel, electric, etc.)")

class VehicleResponse(BaseModel):
    id: int
    vehicle_id: str
    type: str
    capacity_weight: float
    capacity_volume: float
    fuel_type: str
    status: str
    current_location: Optional[dict]
    created_at: str
    updated_at: str

class RouteOptimizationRequest(BaseModel):
    customers: List[dict] = Field(..., description="List of customer locations")
    vehicles: List[dict] = Field(..., description="Available vehicles")
    depot_location: dict = Field(..., description="Depot coordinates")
    constraints: Optional[dict] = Field(None, description="Optimization constraints")
    objectives: Optional[dict] = Field(None, description="Optimization objectives")

class RouteOptimizationResponse(BaseModel):
    routes: List[dict]
    total_distance: float
    total_time: float
    total_cost: float
    optimization_time: float
    algorithm_used: str
```

#### Vehicle Management Endpoints
```python
@app.post("/api/vehicles", response_model=VehicleResponse)
async def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    """Create a new vehicle in the fleet."""
    try:
        # Check if vehicle_id already exists
        existing_vehicle = db.query(Vehicle).filter(
            Vehicle.vehicle_id == vehicle.vehicle_id
        ).first()
        
        if existing_vehicle:
            raise HTTPException(
                status_code=400, 
                detail="Vehicle ID already exists"
            )
        
        # Create new vehicle
        db_vehicle = Vehicle(**vehicle.dict())
        db.add(db_vehicle)
        db.commit()
        db.refresh(db_vehicle)
        
        return VehicleResponse.from_orm(db_vehicle)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vehicles", response_model=List[VehicleResponse])
async def get_vehicles(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[str] = Query(None, description="Filter by vehicle status"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type"),
    db: Session = Depends(get_db)
):
    """Get list of vehicles with optional filtering."""
    
    query = db.query(Vehicle)
    
    if status:
        query = query.filter(Vehicle.status == status)
    
    if vehicle_type:
        query = query.filter(Vehicle.type == vehicle_type)
    
    vehicles = query.offset(skip).limit(limit).all()
    return [VehicleResponse.from_orm(vehicle) for vehicle in vehicles]

@app.get("/api/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """Get specific vehicle by ID."""
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == vehicle_id
    ).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return VehicleResponse.from_orm(vehicle)

@app.put("/api/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: str, 
    vehicle_update: VehicleCreate, 
    db: Session = Depends(get_db)
):
    """Update vehicle information."""
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == vehicle_id
    ).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Update vehicle fields
    for field, value in vehicle_update.dict().items():
        setattr(vehicle, field, value)
    
    vehicle.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(vehicle)
    
    return VehicleResponse.from_orm(vehicle)

@app.delete("/api/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """Delete vehicle from fleet."""
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == vehicle_id
    ).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db.delete(vehicle)
    db.commit()
    
    return {"message": "Vehicle deleted successfully"}
```

#### Route Optimization Endpoints
```python
@app.post("/api/optimize/routes", response_model=RouteOptimizationResponse)
async def optimize_routes(
    request: RouteOptimizationRequest,
    algorithm: str = Query("genetic_algorithm", description="Optimization algorithm"),
    time_limit: int = Query(300, description="Time limit in seconds")
):
    """Optimize vehicle routes for given customers and constraints."""
    
    try:
        # Initialize route optimizer
        optimizer = pmg.RouteOptimizer(
            algorithm=algorithm,
            time_limit=time_limit
        )
        
        # Set constraints if provided
        if request.constraints:
            optimizer.set_constraints(request.constraints)
        
        # Set objectives if provided
        if request.objectives:
            optimizer.set_objectives(request.objectives)
        
        # Run optimization
        start_time = time.time()
        routes = optimizer.solve(
            customers=request.customers,
            vehicles=request.vehicles,
            depot_location=request.depot_location
        )
        optimization_time = time.time() - start_time
        
        # Calculate summary statistics
        total_distance = sum(route.total_distance for route in routes)
        total_time = sum(route.total_time for route in routes)
        total_cost = sum(route.total_cost for route in routes)
        
        return RouteOptimizationResponse(
            routes=[route.to_dict() for route in routes],
            total_distance=total_distance,
            total_time=total_time,
            total_cost=total_cost,
            optimization_time=optimization_time,
            algorithm_used=algorithm
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Route optimization failed: {str(e)}"
        )

@app.post("/api/optimize/facilities")
async def optimize_facility_locations(
    customers: List[dict],
    candidate_locations: List[dict],
    num_facilities: int = Query(..., ge=1, description="Number of facilities to select"),
    objectives: Optional[dict] = None
):
    """Optimize facility locations for given customer demand."""
    
    try:
        # Initialize facility optimizer
        optimizer = pmg.FacilityLocationOptimizer()
        
        if objectives:
            optimizer.set_objectives(objectives)
        
        # Run optimization
        selected_facilities = optimizer.optimize(
            customers=customers,
            candidate_locations=candidate_locations,
            num_facilities=num_facilities
        )
        
        return {
            "selected_facilities": selected_facilities,
            "total_cost": optimizer.get_total_cost(),
            "service_coverage": optimizer.get_service_coverage(),
            "optimization_summary": optimizer.get_summary()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Facility optimization failed: {str(e)}"
        )
```

### 2. Real-Time API Endpoints

#### WebSocket Implementation
```python
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.vehicle_subscribers: dict = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)
    
    async def send_vehicle_update(self, vehicle_id: str, data: dict):
        message = json.dumps({
            "type": "vehicle_update",
            "vehicle_id": vehicle_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Send to subscribers of this vehicle
        if vehicle_id in self.vehicle_subscribers:
            for websocket in self.vehicle_subscribers[vehicle_id]:
                try:
                    await websocket.send_text(message)
                except:
                    self.vehicle_subscribers[vehicle_id].remove(websocket)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data["type"] == "subscribe_vehicle":
                vehicle_id = message_data["vehicle_id"]
                if vehicle_id not in manager.vehicle_subscribers:
                    manager.vehicle_subscribers[vehicle_id] = []
                manager.vehicle_subscribers[vehicle_id].append(websocket)
                
            elif message_data["type"] == "unsubscribe_vehicle":
                vehicle_id = message_data["vehicle_id"]
                if vehicle_id in manager.vehicle_subscribers:
                    if websocket in manager.vehicle_subscribers[vehicle_id]:
                        manager.vehicle_subscribers[vehicle_id].remove(websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/vehicles/{vehicle_id}/location")
async def update_vehicle_location(
    vehicle_id: str,
    location_data: dict,
    db: Session = Depends(get_db)
):
    """Update vehicle location and broadcast to subscribers."""
    
    # Update database
    vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_id == vehicle_id
    ).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    vehicle.current_location = location_data
    vehicle.updated_at = datetime.utcnow()
    db.commit()
    
    # Broadcast update to WebSocket subscribers
    await manager.send_vehicle_update(vehicle_id, location_data)
    
    return {"message": "Location updated successfully"}
```

### 3. GraphQL API Implementation

#### GraphQL Schema and Resolvers
```python
import strawberry
from typing import List, Optional
import pymapgis as pmg

@strawberry.type
class Vehicle:
    id: int
    vehicle_id: str
    type: str
    capacity_weight: float
    capacity_volume: float
    fuel_type: str
    status: str
    current_location: Optional[str]

@strawberry.type
class Route:
    id: int
    route_name: str
    vehicle_id: str
    total_distance: float
    total_time: float
    total_cost: float
    status: str

@strawberry.type
class Customer:
    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    demand: float

@strawberry.input
class VehicleInput:
    vehicle_id: str
    type: str
    capacity_weight: float
    capacity_volume: float
    fuel_type: str

@strawberry.input
class RouteOptimizationInput:
    customer_ids: List[int]
    vehicle_ids: List[str]
    depot_latitude: float
    depot_longitude: float

@strawberry.type
class Query:
    @strawberry.field
    def vehicles(self, status: Optional[str] = None) -> List[Vehicle]:
        """Get list of vehicles with optional status filter."""
        # Implementation here
        pass
    
    @strawberry.field
    def vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        """Get specific vehicle by ID."""
        # Implementation here
        pass
    
    @strawberry.field
    def routes(self, vehicle_id: Optional[str] = None) -> List[Route]:
        """Get routes with optional vehicle filter."""
        # Implementation here
        pass
    
    @strawberry.field
    def customers(self, limit: int = 100) -> List[Customer]:
        """Get list of customers."""
        # Implementation here
        pass

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_vehicle(self, vehicle_input: VehicleInput) -> Vehicle:
        """Create a new vehicle."""
        # Implementation here
        pass
    
    @strawberry.mutation
    def optimize_routes(self, input: RouteOptimizationInput) -> List[Route]:
        """Optimize routes for given parameters."""
        # Implementation here
        pass
    
    @strawberry.mutation
    def update_vehicle_location(
        self, 
        vehicle_id: str, 
        latitude: float, 
        longitude: float
    ) -> Vehicle:
        """Update vehicle location."""
        # Implementation here
        pass

schema = strawberry.Schema(query=Query, mutation=Mutation)

# Add GraphQL endpoint to FastAPI
from strawberry.fastapi import GraphQLRouter

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
```

### 4. Authentication and Authorization

#### JWT-based Authentication
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Security configuration
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user from database
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Role-based authorization
def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Protected endpoints
@app.post("/api/vehicles", dependencies=[Depends(require_role("admin"))])
async def create_vehicle_protected(vehicle: VehicleCreate):
    """Create vehicle - admin only."""
    pass

@app.get("/api/vehicles", dependencies=[Depends(get_current_user)])
async def get_vehicles_protected():
    """Get vehicles - authenticated users only."""
    pass
```

### 5. API Documentation and Testing

#### Automated API Documentation
```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="PyMapGIS Logistics API",
        version="1.0.0",
        description="""
        Comprehensive logistics and supply chain management API.
        
        ## Features
        
        * **Vehicle Management**: Complete fleet management capabilities
        * **Route Optimization**: Advanced routing algorithms
        * **Real-time Tracking**: Live vehicle and shipment tracking
        * **Analytics**: Performance metrics and reporting
        * **Integration**: Enterprise system connectivity
        
        ## Authentication
        
        This API uses JWT tokens for authentication. Include the token in the Authorization header:
        
        ```
        Authorization: Bearer <your-token>
        ```
        """,
        routes=app.routes,
    )
    
    # Add custom tags
    openapi_schema["tags"] = [
        {
            "name": "vehicles",
            "description": "Vehicle fleet management operations"
        },
        {
            "name": "routes",
            "description": "Route planning and optimization"
        },
        {
            "name": "tracking",
            "description": "Real-time tracking and monitoring"
        },
        {
            "name": "analytics",
            "description": "Performance analytics and reporting"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# API testing endpoints
@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/status")
async def system_status():
    """Detailed system status for diagnostics."""
    return {
        "api_status": "operational",
        "database_status": "connected",
        "cache_status": "operational",
        "external_services": {
            "traffic_api": "connected",
            "weather_api": "connected",
            "geocoding_api": "connected"
        },
        "performance_metrics": {
            "avg_response_time": "150ms",
            "requests_per_minute": 1250,
            "error_rate": "0.1%"
        }
    }
```

### 6. API Performance and Monitoring

#### Performance Optimization
```python
from fastapi import BackgroundTasks
import asyncio
from functools import lru_cache
import redis

# Redis cache for performance
redis_client = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=128)
def get_cached_route_calculation(start_lat, start_lon, end_lat, end_lon):
    """Cache expensive route calculations."""
    cache_key = f"route:{start_lat}:{start_lon}:{end_lat}:{end_lon}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        return json.loads(cached_result)
    
    # Perform calculation
    result = calculate_route(start_lat, start_lon, end_lat, end_lon)
    
    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(result))
    
    return result

# Background task processing
@app.post("/api/optimize/routes/async")
async def optimize_routes_async(
    request: RouteOptimizationRequest,
    background_tasks: BackgroundTasks
):
    """Start route optimization as background task."""
    
    task_id = str(uuid.uuid4())
    
    # Store task status
    redis_client.setex(f"task:{task_id}", 3600, json.dumps({
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }))
    
    # Add background task
    background_tasks.add_task(
        process_route_optimization, 
        task_id, 
        request
    )
    
    return {"task_id": task_id, "status": "pending"}

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get background task status."""
    
    task_data = redis_client.get(f"task:{task_id}")
    
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return json.loads(task_data)

async def process_route_optimization(task_id: str, request: RouteOptimizationRequest):
    """Background task for route optimization."""
    
    try:
        # Update status to processing
        redis_client.setex(f"task:{task_id}", 3600, json.dumps({
            "status": "processing",
            "started_at": datetime.utcnow().isoformat()
        }))
        
        # Perform optimization
        optimizer = pmg.RouteOptimizer()
        routes = optimizer.solve(
            customers=request.customers,
            vehicles=request.vehicles,
            depot_location=request.depot_location
        )
        
        # Update status to completed
        redis_client.setex(f"task:{task_id}", 3600, json.dumps({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "result": [route.to_dict() for route in routes]
        }))
        
    except Exception as e:
        # Update status to failed
        redis_client.setex(f"task:{task_id}", 3600, json.dumps({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }))
```

### 7. Enterprise Integration Patterns

#### ERP System Integration
```python
class ERPIntegration:
    def __init__(self, erp_config):
        self.erp_client = ERPClient(erp_config)
        self.sync_interval = 300  # 5 minutes
    
    async def sync_with_erp(self):
        """Synchronize data with ERP system."""
        
        try:
            # Sync customers
            erp_customers = await self.erp_client.get_customers()
            await self.sync_customers(erp_customers)
            
            # Sync orders
            erp_orders = await self.erp_client.get_orders()
            await self.sync_orders(erp_orders)
            
            # Sync inventory
            erp_inventory = await self.erp_client.get_inventory()
            await self.sync_inventory(erp_inventory)
            
            # Send logistics updates back to ERP
            await self.send_logistics_updates()
            
        except Exception as e:
            logger.error(f"ERP sync error: {e}")
    
    async def sync_customers(self, erp_customers):
        """Sync customer data from ERP."""
        for erp_customer in erp_customers:
            # Check if customer exists
            existing_customer = await self.get_customer_by_erp_id(
                erp_customer['id']
            )
            
            if existing_customer:
                # Update existing customer
                await self.update_customer(existing_customer, erp_customer)
            else:
                # Create new customer
                await self.create_customer_from_erp(erp_customer)

@app.post("/api/integration/erp/webhook")
async def erp_webhook(webhook_data: dict):
    """Handle ERP system webhooks."""
    
    event_type = webhook_data.get('event_type')
    
    if event_type == 'order_created':
        await handle_new_order(webhook_data['order'])
    elif event_type == 'customer_updated':
        await handle_customer_update(webhook_data['customer'])
    elif event_type == 'inventory_changed':
        await handle_inventory_change(webhook_data['inventory'])
    
    return {"status": "processed"}
```

---

*This comprehensive API development guide provides complete coverage of RESTful APIs, GraphQL, real-time APIs, authentication, and enterprise integration patterns for PyMapGIS logistics applications.*
