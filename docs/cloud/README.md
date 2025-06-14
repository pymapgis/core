# ☁️ PyMapGIS Cloud Integration

PyMapGIS provides seamless cloud-native integration with major cloud storage providers, enabling direct access to geospatial data without local downloads.

## 🌟 Cloud-Native Features

### **🔗 Multi-Cloud Support**
- **Amazon S3**: Direct S3 bucket access with IAM integration
- **Google Cloud Storage**: GCS bucket support with service account auth
- **Azure Blob Storage**: Azure container access with managed identity
- **S3-Compatible**: MinIO, DigitalOcean Spaces, and other S3-compatible services

### **⚡ Performance Optimizations**
- **Smart Caching**: Intelligent cache invalidation based on object timestamps
- **Streaming Access**: Process large files without downloading
- **Parallel Processing**: Multi-threaded operations for large datasets
- **Windowed Reading**: Access specific regions of large raster files

### **🔧 Cloud-Optimized Formats**
- **Cloud Optimized GeoTIFF (COG)**: Efficient raster access
- **GeoParquet**: Columnar vector data with spatial indexing
- **Zarr**: Multidimensional arrays with chunking
- **FlatGeobuf**: Streaming vector data format

## 🚀 Quick Start

### **Installation**
```bash
# Install cloud dependencies
pip install pymapgis[cloud]

# Or install specific providers
pip install boto3  # AWS S3
pip install google-cloud-storage  # Google Cloud
pip install azure-storage-blob  # Azure
```

### **Basic Usage**
```python
import pymapgis as pmg

# Direct cloud data access
gdf = pmg.cloud_read("s3://your-bucket/data.geojson")
raster = pmg.cloud_read("gs://your-bucket/satellite.cog")
zarr_data = pmg.cloud_read("azure://container/timeseries.zarr")

# Process without downloading
result = gdf.buffer(1000)  # Operations work directly on cloud data

# Save back to cloud
pmg.cloud_write(result, "s3://your-bucket/processed.geojson")
```

## 🔧 Provider Setup

### **Amazon S3**
```python
# Method 1: Environment variables
import os
os.environ["AWS_ACCESS_KEY_ID"] = "your-access-key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "your-secret-key"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# Method 2: Explicit configuration
pmg.cloud.configure_s3(
    access_key="your-access-key",
    secret_key="your-secret-key",
    region="us-east-1"
)

# Method 3: IAM roles (recommended for EC2/Lambda)
# No configuration needed - uses instance profile
```

### **Google Cloud Storage**
```python
# Method 1: Service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/credentials.json"

# Method 2: Explicit configuration
pmg.cloud.configure_gcs(
    credentials_path="/path/to/credentials.json",
    project_id="your-project-id"
)

# Method 3: Default credentials (recommended for GCE/Cloud Run)
# No configuration needed - uses default service account
```

### **Azure Blob Storage**
```python
# Method 1: Connection string
os.environ["AZURE_STORAGE_CONNECTION_STRING"] = "your-connection-string"

# Method 2: Account key
pmg.cloud.configure_azure(
    account_name="your-account",
    account_key="your-key"
)

# Method 3: Managed identity (recommended for Azure VMs)
pmg.cloud.configure_azure(
    account_name="your-account",
    use_managed_identity=True
)
```

## 📊 Advanced Usage

### **High-Performance Processing**
```python
# Async processing for large datasets
async with pmg.AsyncGeoProcessor() as processor:
    # Process multiple cloud files in parallel
    results = await processor.process_cloud_files([
        "s3://bucket/file1.geojson",
        "s3://bucket/file2.geojson",
        "s3://bucket/file3.geojson"
    ])

# Streaming processing for massive files
for chunk in pmg.cloud_stream("s3://bucket/massive-dataset.parquet"):
    processed_chunk = process_chunk(chunk)
    pmg.cloud_write(processed_chunk, f"s3://bucket/processed/{chunk.id}.parquet")
```

### **Smart Caching**
```python
# Configure intelligent caching
pmg.cloud.configure_cache(
    cache_dir="/tmp/pymapgis-cache",
    max_size_gb=10,
    ttl_hours=24,
    enable_smart_invalidation=True
)

# Cache will automatically invalidate when cloud objects change
data = pmg.cloud_read("s3://bucket/data.geojson")  # Downloads and caches
data = pmg.cloud_read("s3://bucket/data.geojson")  # Uses cache (instant)

# After file is updated in S3, cache automatically invalidates
data = pmg.cloud_read("s3://bucket/data.geojson")  # Re-downloads updated file
```

### **Windowed Raster Access**
```python
# Access specific regions of large raster files
raster = pmg.cloud_read("s3://bucket/large-satellite-image.cog")

# Read only a specific window (no full download!)
window_data = raster.read_window(
    x_min=1000, y_min=1000,
    x_max=2000, y_max=2000
)

# Resample to different resolution
resampled = raster.read_resampled(
    target_resolution=30,  # 30m pixels
    resampling_method="bilinear"
)
```

## 🔒 Security Best Practices

### **Credential Management**
```python
# ✅ Good: Use environment variables
os.environ["AWS_ACCESS_KEY_ID"] = "your-key"

# ✅ Better: Use IAM roles/managed identity
# No credentials in code

# ❌ Bad: Hardcode credentials
pmg.cloud.configure_s3(access_key="AKIAIOSFODNN7EXAMPLE")  # Don't do this!
```

### **Access Control**
```python
# Use least-privilege IAM policies
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::your-bucket/data/*"
        }
    ]
}
```

## 🚀 Production Deployment

### **Docker Configuration**
```dockerfile
FROM python:3.11-slim

# Install cloud dependencies
RUN pip install pymapgis[cloud]

# Copy application
COPY . /app
WORKDIR /app

# Use environment variables for credentials
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/gcs-credentials.json"

CMD ["python", "app.py"]
```

### **Kubernetes Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pymapgis-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pymapgis-app
  template:
    metadata:
      labels:
        app: pymapgis-app
    spec:
      containers:
      - name: app
        image: your-registry/pymapgis-app:latest
        env:
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: access-key-id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: secret-access-key
```

## 📈 Performance Optimization

### **Caching Strategies**
```python
# Configure multi-level caching
pmg.cloud.configure_cache(
    # Local disk cache
    local_cache_dir="/tmp/pymapgis-cache",
    local_cache_size_gb=10,
    
    # Redis cache for shared environments
    redis_url="redis://localhost:6379",
    redis_ttl_hours=24,
    
    # Memory cache for frequently accessed data
    memory_cache_size_mb=512
)
```

### **Parallel Processing**
```python
# Process multiple cloud files in parallel
from concurrent.futures import ThreadPoolExecutor

def process_file(url):
    return pmg.cloud_read(url).buffer(1000)

urls = [
    "s3://bucket/file1.geojson",
    "s3://bucket/file2.geojson",
    "s3://bucket/file3.geojson"
]

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_file, urls))
```

## 🔍 Monitoring & Debugging

### **Enable Logging**
```python
import logging

# Enable cloud operation logging
logging.getLogger("pymapgis.cloud").setLevel(logging.INFO)

# Enable performance metrics
pmg.cloud.enable_metrics(
    log_performance=True,
    track_cache_hits=True,
    monitor_bandwidth=True
)
```

### **Health Checks**
```python
# Check cloud connectivity
health = pmg.cloud.health_check()
print(f"S3 Status: {health['s3']}")
print(f"GCS Status: {health['gcs']}")
print(f"Azure Status: {health['azure']}")

# Performance metrics
metrics = pmg.cloud.get_metrics()
print(f"Cache Hit Rate: {metrics['cache_hit_rate']:.2%}")
print(f"Average Download Speed: {metrics['avg_download_speed_mbps']:.1f} Mbps")
```

## 💡 Use Cases

### **Data Pipeline**
```python
# ETL pipeline with cloud data
def process_daily_data():
    # Extract from multiple sources
    weather = pmg.cloud_read("s3://weather-data/daily/2024-01-15.zarr")
    traffic = pmg.cloud_read("gs://traffic-data/2024-01-15.geojson")
    
    # Transform
    combined = pmg.spatial_join(weather, traffic)
    aggregated = combined.groupby("region").agg({
        "temperature": "mean",
        "traffic_volume": "sum"
    })
    
    # Load to data warehouse
    pmg.cloud_write(aggregated, "azure://warehouse/processed/2024-01-15.parquet")
```

### **Real-Time Analytics**
```python
# Stream processing with cloud storage
for event in pmg.streaming.read("kafka://sensor-data"):
    # Process real-time sensor data
    processed = process_sensor_event(event)
    
    # Store in cloud for batch processing
    pmg.cloud_append(processed, "s3://sensor-archive/hourly/")
    
    # Update real-time dashboard
    update_dashboard(processed)
```

## 🤝 Contributing

We welcome contributions to improve cloud integration:

1. **Add new providers**: Implement support for additional cloud storage services
2. **Optimize performance**: Improve caching and streaming algorithms
3. **Enhance security**: Add new authentication methods
4. **Improve documentation**: Add examples and best practices

See [Contributing Guide](../CONTRIBUTING.md) for details.

---

**Transform your geospatial workflows with cloud-native PyMapGIS!** ☁️🚀
