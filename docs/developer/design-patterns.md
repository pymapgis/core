# 🎨 Design Patterns

## Overview

PyMapGIS employs several key design patterns to ensure consistency, maintainability, and extensibility. This document outlines the primary patterns used throughout the codebase and provides guidance for developers on when and how to apply them.

## Core Patterns

### 1. Plugin Architecture Pattern

**Purpose**: Enable extensible functionality without modifying core code

**Implementation**:
```python
# Base plugin interface
class DataSourcePlugin(ABC):
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        pass
    
    @abstractmethod
    def read(self, url: str, **kwargs) -> Union[GeoDataFrame, DataArray]:
        pass

# Plugin registry
class PluginRegistry:
    def __init__(self):
        self._plugins = []
    
    def register(self, plugin: DataSourcePlugin):
        self._plugins.append(plugin)
    
    def find_plugin(self, url: str) -> Optional[DataSourcePlugin]:
        for plugin in self._plugins:
            if plugin.can_handle(url):
                return plugin
        return None
```

**Usage Examples**:
- Data source plugins (`census://`, `tiger://`, `s3://`)
- Format handlers (GeoJSON, Shapefile, GeoTIFF)
- Authentication providers (OAuth, API keys)
- Visualization backends (Leafmap, Matplotlib)

### 2. Accessor Pattern

**Purpose**: Extend existing classes with domain-specific functionality

**Implementation**:
```python
@pd.api.extensions.register_dataframe_accessor("pmg")
class PyMapGISAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
    
    def buffer(self, distance, **kwargs):
        """Buffer geometries in the GeoDataFrame."""
        return buffer(self._obj, distance, **kwargs)
    
    def clip(self, mask, **kwargs):
        """Clip GeoDataFrame to mask boundaries."""
        return clip(self._obj, mask, **kwargs)
```

**Usage Examples**:
- `.pmg` accessor for GeoDataFrames (vector operations)
- `.pmg` accessor for DataArrays (raster operations)
- `.pmg` accessor for visualization methods

### 3. Factory Pattern

**Purpose**: Create objects without specifying exact classes

**Implementation**:
```python
class DataSourceFactory:
    _plugins = {}
    
    @classmethod
    def register_plugin(cls, scheme: str, plugin_class: Type[DataSourcePlugin]):
        cls._plugins[scheme] = plugin_class
    
    @classmethod
    def create_plugin(cls, url: str) -> DataSourcePlugin:
        scheme = urlparse(url).scheme
        if scheme in cls._plugins:
            return cls._plugins[scheme]()
        raise ValueError(f"No plugin for scheme: {scheme}")
```

**Usage Examples**:
- Data source creation based on URL scheme
- Cache backend selection
- Authentication provider instantiation
- Service endpoint creation

### 4. Strategy Pattern

**Purpose**: Define family of algorithms and make them interchangeable

**Implementation**:
```python
class CachingStrategy(ABC):
    @abstractmethod
    def should_cache(self, url: str, data_size: int) -> bool:
        pass
    
    @abstractmethod
    def get_ttl(self, url: str) -> int:
        pass

class AggressiveCaching(CachingStrategy):
    def should_cache(self, url: str, data_size: int) -> bool:
        return data_size < 100_000_000  # Cache if < 100MB
    
    def get_ttl(self, url: str) -> int:
        return 3600  # 1 hour

class ConservativeCaching(CachingStrategy):
    def should_cache(self, url: str, data_size: int) -> bool:
        return data_size < 10_000_000  # Cache if < 10MB
    
    def get_ttl(self, url: str) -> int:
        return 1800  # 30 minutes
```

**Usage Examples**:
- Caching strategies (aggressive, conservative, disabled)
- Spatial indexing algorithms (R-tree, Grid, KD-tree)
- Reprojection methods (PROJ, pyproj, custom)
- Tile generation strategies (on-demand, pre-generated)

### 5. Observer Pattern

**Purpose**: Define one-to-many dependency between objects

**Implementation**:
```python
class CacheObserver(ABC):
    @abstractmethod
    def on_cache_hit(self, key: str, size: int):
        pass
    
    @abstractmethod
    def on_cache_miss(self, key: str):
        pass

class CacheManager:
    def __init__(self):
        self._observers = []
    
    def add_observer(self, observer: CacheObserver):
        self._observers.append(observer)
    
    def _notify_hit(self, key: str, size: int):
        for observer in self._observers:
            observer.on_cache_hit(key, size)
```

**Usage Examples**:
- Cache event monitoring
- Progress tracking for long operations
- Performance metrics collection
- Error reporting and logging

### 6. Decorator Pattern

**Purpose**: Add behavior to objects dynamically

**Implementation**:
```python
def cache_result(ttl: int = 3600):
    """Decorator to cache function results."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash((args, tuple(kwargs.items())))}"
            
            # Check cache
            if cache_key in cache:
                return cache[cache_key]
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache[cache_key] = result
            return result
        return wrapper
    return decorator

@cache_result(ttl=1800)
def expensive_operation(data):
    # Expensive computation
    return result
```

**Usage Examples**:
- Result caching (`@cache_result`)
- Performance timing (`@time_execution`)
- Authentication required (`@require_auth`)
- Rate limiting (`@rate_limit`)

### 7. Builder Pattern

**Purpose**: Construct complex objects step by step

**Implementation**:
```python
class MapBuilder:
    def __init__(self):
        self._map = None
        self._layers = []
        self._style = {}
    
    def create_map(self, center=None, zoom=None):
        self._map = leafmap.Map(center=center, zoom=zoom)
        return self
    
    def add_layer(self, data, name=None, style=None):
        self._layers.append({
            'data': data,
            'name': name,
            'style': style or {}
        })
        return self
    
    def set_style(self, **style_options):
        self._style.update(style_options)
        return self
    
    def build(self):
        for layer in self._layers:
            self._map.add_gdf(
                layer['data'],
                layer=layer['name'],
                style=layer['style']
            )
        return self._map
```

**Usage Examples**:
- Interactive map construction
- Complex query building
- Service configuration
- Pipeline construction

## Functional Patterns

### 8. Fluent Interface Pattern

**Purpose**: Create readable, chainable APIs

**Implementation**:
```python
# Chainable operations via accessor
result = (counties
    .pmg.clip(study_area)
    .pmg.buffer(1000)
    .pmg.spatial_join(demographics)
    .pmg.explore(column='population'))

# Chainable map building
map_obj = (pmg.Map()
    .add_layer(counties, name='Counties')
    .add_layer(cities, name='Cities')
    .set_style(color='blue', weight=2)
    .build())
```

**Benefits**:
- Improved readability
- Reduced intermediate variables
- Natural workflow expression
- IDE autocomplete support

### 9. Lazy Evaluation Pattern

**Purpose**: Defer computation until results are needed

**Implementation**:
```python
class LazyDataFrame:
    def __init__(self, url, **kwargs):
        self._url = url
        self._kwargs = kwargs
        self._data = None
    
    @property
    def data(self):
        if self._data is None:
            self._data = self._load_data()
        return self._data
    
    def _load_data(self):
        return pmg.read(self._url, **self._kwargs)
    
    def __getattr__(self, name):
        return getattr(self.data, name)
```

**Usage Examples**:
- Lazy data loading
- Deferred computation chains
- Optional dependency imports
- Large dataset processing

### 10. Pipeline Pattern

**Purpose**: Process data through sequence of transformations

**Implementation**:
```python
class GeoProcessingPipeline:
    def __init__(self):
        self._steps = []
    
    def add_step(self, func, *args, **kwargs):
        self._steps.append((func, args, kwargs))
        return self
    
    def execute(self, data):
        result = data
        for func, args, kwargs in self._steps:
            result = func(result, *args, **kwargs)
        return result

# Usage
pipeline = (GeoProcessingPipeline()
    .add_step(pmg.vector.clip, mask=study_area)
    .add_step(pmg.vector.buffer, distance=1000)
    .add_step(pmg.vector.spatial_join, right_df=demographics))

result = pipeline.execute(counties)
```

## Error Handling Patterns

### 11. Exception Chaining Pattern

**Purpose**: Preserve error context while adding domain-specific information

**Implementation**:
```python
class DataSourceError(PyMapGISError):
    """Error in data source operations."""
    pass

def read_census_data(url):
    try:
        response = requests.get(census_api_url)
        response.raise_for_status()
        return process_response(response)
    except requests.RequestException as e:
        raise DataSourceError(
            f"Failed to fetch Census data from {url}"
        ) from e
    except ValueError as e:
        raise DataSourceError(
            f"Invalid Census API response format"
        ) from e
```

### 12. Retry Pattern

**Purpose**: Handle transient failures gracefully

**Implementation**:
```python
def retry_on_failure(max_retries=3, delay=1.0, backoff=2.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, ConnectionError) as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(delay * (backoff ** attempt))
                    continue
            
            raise last_exception
        return wrapper
    return decorator
```

## Performance Patterns

### 13. Memoization Pattern

**Purpose**: Cache expensive function results

**Implementation**:
```python
from functools import lru_cache

class SpatialIndex:
    @lru_cache(maxsize=128)
    def build_index(self, geometry_hash):
        """Build spatial index for geometries."""
        return self._create_rtree_index()
    
    def query(self, geometries, bounds):
        geom_hash = hash(tuple(geom.wkt for geom in geometries))
        index = self.build_index(geom_hash)
        return index.intersection(bounds)
```

### 14. Object Pool Pattern

**Purpose**: Reuse expensive objects

**Implementation**:
```python
class ConnectionPool:
    def __init__(self, max_connections=10):
        self._pool = queue.Queue(maxsize=max_connections)
        self._max_connections = max_connections
        self._created_connections = 0
    
    def get_connection(self):
        try:
            return self._pool.get_nowait()
        except queue.Empty:
            if self._created_connections < self._max_connections:
                conn = self._create_connection()
                self._created_connections += 1
                return conn
            else:
                return self._pool.get()  # Block until available
    
    def return_connection(self, conn):
        self._pool.put(conn)
```

## Testing Patterns

### 15. Test Fixture Pattern

**Purpose**: Provide consistent test data and setup

**Implementation**:
```python
@pytest.fixture
def sample_counties():
    """Provide sample county data for testing."""
    return gpd.GeoDataFrame({
        'name': ['County A', 'County B'],
        'population': [100000, 200000],
        'geometry': [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])
        ]
    })

@pytest.fixture
def mock_census_api():
    """Mock Census API responses."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            'https://api.census.gov/data/2022/acs/acs5',
            json={'data': [['County A', '100000']]},
            status=200
        )
        yield rsps
```

### 16. Mock Pattern

**Purpose**: Replace dependencies with controlled implementations

**Implementation**:
```python
class MockDataSource:
    def __init__(self, return_data):
        self.return_data = return_data
        self.call_count = 0
    
    def read(self, url, **kwargs):
        self.call_count += 1
        return self.return_data
    
    def __enter__(self):
        # Replace real data source
        original_read = pmg.read
        pmg.read = self.read
        self._original_read = original_read
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original
        pmg.read = self._original_read
```

## Best Practices

### Pattern Selection Guidelines

1. **Plugin Architecture**: Use for extensible functionality
2. **Accessor Pattern**: Use for extending existing classes
3. **Factory Pattern**: Use when object creation is complex
4. **Strategy Pattern**: Use for interchangeable algorithms
5. **Observer Pattern**: Use for event-driven architectures
6. **Decorator Pattern**: Use for cross-cutting concerns
7. **Builder Pattern**: Use for complex object construction

### Implementation Guidelines

1. **Consistency**: Use patterns consistently across the codebase
2. **Documentation**: Document pattern usage and rationale
3. **Testing**: Test pattern implementations thoroughly
4. **Performance**: Consider performance implications
5. **Simplicity**: Don't over-engineer with unnecessary patterns

### Anti-Patterns to Avoid

1. **God Object**: Avoid classes that do too much
2. **Spaghetti Code**: Maintain clear separation of concerns
3. **Copy-Paste**: Use patterns to reduce code duplication
4. **Premature Optimization**: Don't optimize without profiling
5. **Over-Engineering**: Keep solutions as simple as possible

---

*Next: [Data Flow](./data-flow.md) for understanding how data moves through PyMapGIS*
