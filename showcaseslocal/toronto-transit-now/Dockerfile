# Toronto Transit Now - Optimized Docker Configuration
# Uses the PyMapGIS base image for lightning-fast builds

FROM nicholaskarlson/pymapgis-base:latest

# Set working directory (inherited from base)
WORKDIR /app

# Copy application files only (dependencies already installed in base image)
COPY showcaseslocal/toronto-transit-now/transit_worker.py showcaseslocal/toronto-transit-now/app.py ./
COPY showcaseslocal/toronto-transit-now/static/ ./static/
COPY showcaseslocal/toronto-transit-now/data/ ./data/

# Create transit-specific user (override base user)
USER root
RUN useradd --create-home --shell /bin/bash ttctransit && \
    chown -R ttctransit:ttctransit /app

# Switch to transit-specific user
USER ttctransit

# Expose port (inherited from base)
EXPOSE 8000

# Transit-specific health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the Toronto transit application
CMD ["python", "-c", "import subprocess; import sys; subprocess.run([sys.executable, 'transit_worker.py']); import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8000)"]
