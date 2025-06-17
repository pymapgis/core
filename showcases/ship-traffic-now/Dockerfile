# Ship Traffic Now - Optimized Docker Configuration
# Uses the new PyMapGIS base image for dramatically faster builds

FROM nicholaskarlson/pymapgis-base:latest

# Set working directory (inherited from base)
WORKDIR /app

# Copy application files only (dependencies already installed in base image)
COPY showcases/ship-traffic-now/ship_worker.py showcases/ship-traffic-now/app.py ./
COPY showcases/ship-traffic-now/static/ ./static/
COPY showcases/ship-traffic-now/data/ ./data/

# Create ship-specific user (override base user)
USER root
RUN useradd --create-home --shell /bin/bash shiptraffic && \
    chown -R shiptraffic:shiptraffic /app

# Switch to ship-specific user
USER shiptraffic

# Expose port (inherited from base)
EXPOSE 8000

# Ship-specific health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the ship traffic application
CMD ["python", "-c", "import subprocess; import sys; subprocess.run([sys.executable, 'ship_worker.py']); import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8000)"]
