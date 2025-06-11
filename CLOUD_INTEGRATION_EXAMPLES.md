# PyMapGIS Cloud-Native Integration - Phase 3 Feature

## ☁️ **Seamless Cloud Storage Integration**

PyMapGIS Phase 3 introduces comprehensive cloud-native capabilities that enable direct access to geospatial data stored in major cloud platforms:

- **Amazon S3** (AWS)
- **Google Cloud Storage** (GCS)
- **Azure Blob Storage**
- **S3-Compatible Storage** (MinIO, DigitalOcean Spaces, etc.)

---

## 🚀 **Key Features**

### **Unified Cloud API**
- Single interface for all cloud providers
- Automatic credential detection
- Intelligent caching and optimization
- Cloud-optimized data formats

### **Performance Benefits**
- **Direct cloud access** without local downloads
- **Streaming data processing** for large files
- **Intelligent caching** with automatic invalidation
- **Parallel chunk processing** for cloud datasets

### **Cloud-Optimized Formats**
- **Cloud Optimized GeoTIFF (COG)** for raster data
- **GeoParquet** for vector data
- **Zarr** for multidimensional arrays
- **FlatGeobuf** for streaming vector data

---

## 📊 **Quick Start Examples**

### **1. Reading Data from Cloud Storage**

```python
import pymapgis as pmg

# Read directly from S3
gdf = pmg.cloud_read("s3://my-bucket/cities.geojson")

# Read from Google Cloud Storage
df = pmg.cloud_read("gs://my-bucket/census_data.csv")

# Read from Azure Blob Storage
raster = pmg.cloud_read("https://account.blob.core.windows.net/container/elevation.tif")

print(f"Loaded {len(gdf)} features from cloud storage")
```

### **2. Writing Data to Cloud Storage**

```python
import pymapgis as pmg
import geopandas as gpd

# Create some sample data
gdf = gpd.read_file("local_data.geojson")

# Write to S3
pmg.cloud_write(gdf, "s3://my-bucket/processed_data.geojson")

# Write to GCS as GeoParquet (cloud-optimized)
pmg.cloud_write(gdf, "gs://my-bucket/processed_data.parquet")

# Write to Azure
pmg.cloud_write(gdf, "https://account.blob.core.windows.net/container/output.gpkg")
```

### **3. Cloud Provider Registration**

```python
import pymapgis as pmg
from pymapgis.cloud import register_s3_provider, register_gcs_provider

# Register S3 provider with specific configuration
s3_provider = register_s3_provider(
    name="my_s3",
    bucket="my-data-bucket",
    region="us-west-2"
)

# Register GCS provider
gcs_provider = register_gcs_provider(
    name="my_gcs",
    bucket="my-gcs-bucket",
    project="my-project-id"
)

# Use registered providers
gdf = pmg.cloud_read("s3://my-data-bucket/data.geojson", provider_name="my_s3")
```

---

## 🛠 **Advanced Cloud Operations**

### **4. Cloud File Management**

```python
import pymapgis as pmg

# List files in cloud storage
files = pmg.list_cloud_files("s3://my-bucket/geospatial/")
for file_info in files:
    print(f"{file_info['path']}: {file_info['size']} bytes, modified {file_info['modified']}")

# Get detailed file information
info = pmg.get_cloud_info("s3://my-bucket/large_dataset.parquet")
print(f"File size: {info['size']} bytes")
print(f"Last modified: {info['modified']}")
print(f"Storage class: {info['storage_class']}")
```

### **5. Cloud-Optimized Format Conversion**

```python
from pymapgis.cloud.formats import optimize_for_cloud, convert_to_geoparquet

# Convert local data to cloud-optimized formats
results = optimize_for_cloud(
    input_path="large_dataset.shp",
    output_dir="cloud_optimized/",
    formats=['geoparquet', 'flatgeobuf']
)

print(f"Created optimized formats: {list(results.keys())}")

# Convert specific format
convert_to_geoparquet("cities.geojson", "cities_optimized.parquet")
```

### **6. Streaming Large Cloud Datasets**

```python
import asyncio
import pymapgis as pmg

async def process_large_cloud_dataset():
    """Process large cloud dataset in chunks."""
    
    # Use async processing with cloud data
    processor = pmg.AsyncGeoProcessor()
    
    def analyze_chunk(chunk):
        """Analyze each chunk of data."""
        # Perform analysis on chunk
        chunk['area'] = chunk.geometry.area
        return chunk[chunk['area'] > 1000]  # Filter large features
    
    # Process cloud data in chunks
    result = await processor.process_large_dataset(
        filepath="s3://my-bucket/massive_dataset.parquet",
        operation=analyze_chunk,
        chunk_size=50000,
        show_progress=True
    )
    
    # Write results back to cloud
    pmg.cloud_write(result, "s3://my-bucket/analysis_results.parquet")
    
    await processor.close()

# Run async processing
asyncio.run(process_large_cloud_dataset())
```

---

## 🔧 **Cloud Provider Setup**

### **Amazon S3 Setup**

```bash
# Install AWS CLI and configure credentials
pip install boto3
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

```python
# Use in PyMapGIS
from pymapgis.cloud import S3Storage

s3 = S3Storage(bucket="my-bucket", region="us-west-2")
files = s3.list_files(prefix="geospatial/")
```

### **Google Cloud Storage Setup**

```bash
# Install GCS client and authenticate
pip install google-cloud-storage
gcloud auth application-default login

# Or set service account key
export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

```python
# Use in PyMapGIS
from pymapgis.cloud import GCSStorage

gcs = GCSStorage(bucket="my-bucket", project="my-project")
info = gcs.get_file_info("data/cities.geojson")
```

### **Azure Blob Storage Setup**

```bash
# Install Azure SDK
pip install azure-storage-blob azure-identity

# Set connection string or use Azure CLI
export AZURE_STORAGE_CONNECTION_STRING=your_connection_string
az login
```

```python
# Use in PyMapGIS
from pymapgis.cloud import AzureStorage

azure = AzureStorage(
    account_name="myaccount",
    container="mycontainer",
    account_key="your_account_key"  # Optional, can use default credentials
)
```

---

## 📈 **Performance Optimization**

### **Cloud-Optimized Data Formats**

```python
from pymapgis.cloud.formats import CloudOptimizedWriter, CloudOptimizedReader

# Write Cloud Optimized GeoTIFF
writer = CloudOptimizedWriter()
writer.write_cog(raster_data, "s3://bucket/optimized.tif", 
                 blockxsize=512, blockysize=512, compress='lzw')

# Read with spatial filtering
reader = CloudOptimizedReader()
windowed_data = reader.read_cog_window(
    "s3://bucket/large_raster.tif",
    window=(1000, 1000, 2000, 2000),  # Pixel coordinates
    overview_level=1  # Use overview for faster access
)
```

### **Intelligent Caching**

```python
from pymapgis.cloud import CloudDataReader

# Configure caching
reader = CloudDataReader(cache_dir="/tmp/pymapgis_cache")

# First read downloads and caches
gdf1 = reader.read_cloud_file("s3://bucket/data.parquet")

# Second read uses cache (much faster)
gdf2 = reader.read_cloud_file("s3://bucket/data.parquet")
```

---

## 🎯 **Use Cases**

### **Perfect for:**
- ✅ **Large-scale geospatial analysis** on cloud-stored datasets
- ✅ **Collaborative workflows** with shared cloud storage
- ✅ **Serverless processing** with cloud functions
- ✅ **Data pipelines** with cloud-native formats
- ✅ **Cost optimization** through intelligent caching
- ✅ **Global data access** without data movement

### **Performance Benefits:**
- **No local storage required** for large datasets
- **Parallel processing** of cloud data chunks
- **Automatic format optimization** for cloud access
- **Intelligent caching** reduces redundant downloads
- **Direct streaming** for memory-efficient processing

---

## 🔐 **Security & Best Practices**

### **Credential Management**
```python
# Use environment variables (recommended)
import os
os.environ['AWS_ACCESS_KEY_ID'] = 'your_key'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_secret'

# Use IAM roles (AWS) or service accounts (GCS) in production
# Avoid hardcoding credentials in code
```

### **Cost Optimization**
```python
# Use appropriate storage classes
s3_provider = S3Storage(bucket="my-bucket")
files = s3_provider.list_files()

for file_info in files:
    if file_info['storage_class'] == 'GLACIER':
        print(f"Archived file: {file_info['path']}")
```

---

## 🎉 **Integration with Existing PyMapGIS**

Cloud integration works seamlessly with all existing PyMapGIS features:

```python
import pymapgis as pmg

# Read from cloud
gdf = pmg.cloud_read("s3://bucket/cities.geojson")

# Use existing PyMapGIS functions
buffered = pmg.buffer(gdf, distance=1000)
clipped = pmg.clip(buffered, study_area)

# Visualize
clipped.pmg.explore()

# Serve via API
pmg.serve(clipped, port=8000)

# Write results back to cloud
pmg.cloud_write(clipped, "s3://bucket/results.parquet")
```

---

## 🚀 **Summary**

PyMapGIS Cloud-Native Integration provides:

- ☁️ **Universal cloud storage access** (S3, GCS, Azure)
- ⚡ **High-performance cloud data processing**
- 🗂️ **Cloud-optimized data formats** (COG, GeoParquet, Zarr)
- 🧠 **Intelligent caching and optimization**
- 🔒 **Secure credential management**
- 💰 **Cost-effective cloud operations**

**Perfect for modern cloud-native geospatial workflows!**
