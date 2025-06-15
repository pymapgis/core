# {{DEMO_TITLE}} - Docker Image
# Based on PyMapGIS core with additional dependencies for the demo

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for geospatial processing
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libspatialindex-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install Python dependencies
# Note: In production, you might want to copy a requirements.txt file
RUN pip install --no-cache-dir \
    pymapgis>=1.0.0 \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.32.0 \
    geopandas>=1.1.0 \
    pandas>=2.3.0 \
    numpy>=1.24.0 \
    shapely>=2.0.0 \
    rasterio>=1.4.0 \
    mapbox-vector-tile>=2.1.0 \
    mercantile>=1.2.1 \
    rasterstats>=0.19.0 \
    matplotlib>=3.7.0 \
    requests>=2.28.0

# Copy application files
COPY worker.py .
COPY app.py .

# Copy static files if they exist
COPY static/ ./static/

# Create directories for output
RUN mkdir -p tiles/{{LAYER_NAME}} static

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the data processing first, then start the web server
CMD python worker.py && uvicorn app:app --host 0.0.0.0 --port 8000
