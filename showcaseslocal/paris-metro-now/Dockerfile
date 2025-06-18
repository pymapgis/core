# Paris Metro Now - Optimized Docker Configuration
# Uses the PyMapGIS base image for lightning-fast builds

FROM nicholaskarlson/pymapgis-base:latest

# Set working directory (inherited from base)
WORKDIR /app

# Copy application files only (dependencies already installed in base image)
COPY showcaseslocal/paris-metro-now/transit_worker.py showcaseslocal/paris-metro-now/app.py ./
COPY showcaseslocal/paris-metro-now/static/ ./static/
COPY showcaseslocal/paris-metro-now/data/ ./data/

# Create Paris-specific user (override base user)
USER root
RUN useradd --create-home --shell /bin/bash paris && \
    chown -R paris:paris /app

# Switch to Paris-specific user
USER paris

# Expose port (inherited from base)
EXPOSE 8000

# Paris-specific health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the Paris Metro application
CMD ["python", "-c", "import subprocess; import sys; subprocess.run([sys.executable, 'transit_worker.py']); import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8000)"]
