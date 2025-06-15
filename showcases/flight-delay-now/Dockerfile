# Flight Delay Now - Dockerfile
# Compact container ≤ 170 MB as specified

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal for geospatial)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgdal-dev \
    gdal-bin \
    libproj-dev \
    proj-data \
    proj-bin \
    libgeos-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set GDAL environment variables
ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Create necessary directories
RUN mkdir -p tiles/flight

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run initial data fetch and start server
CMD python flight_worker.py && uvicorn app:app --host 0.0.0.0 --port 8000
