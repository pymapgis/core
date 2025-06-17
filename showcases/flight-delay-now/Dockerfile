# Flight Delay Now - Docker Configuration
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for geospatial processing
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY showcases/flight-delay-now/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY showcases/flight-delay-now/flight_worker.py showcases/flight-delay-now/app.py ./
COPY showcases/flight-delay-now/static/ ./static/
COPY showcases/flight-delay-now/data/ ./data/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash flightdelay && \
    chown -R flightdelay:flightdelay /app

# Switch to non-root user
USER flightdelay

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-c", "import subprocess; import sys; subprocess.run([sys.executable, 'flight_worker.py']); import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8000)"]
